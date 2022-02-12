from django.db.models import query
from django.http.response import BadHeaderError, HttpResponse
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from rest_framework import permissions

from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView

from user.models import Account, CreateJob, SavedJob, AppliedJob
from .serializers import *

from .forms import *

# used - for login
class LoginViewAPI(APIView):
	def post(self, request):
		email = request.data['email']
		password = request.data['password']

		user = authenticate(request, username=email, password=password)

		if user is None:
			raise AuthenticationFailed('Email or password is incorrect')
		else:
			token, created = Token.objects.get_or_create(user=user)
			return Response({
					'message': 'success',
					'user_id': user.id,
					'is_admin': user.admin,
					'is_staff': user.staff,
					'is_active': user.is_active,
					'email': email,
					'firstname': user.firstname,
					'lastname': user.lastname,
					'gender': user.gender,
					'phone': user.phone,
					'token': token.key})

# used - to update account settings
class UpdateAccountViewAPI(APIView):
	permission_classes = (IsAuthenticated,)
	def post(self, request):
		id = request.data['id']
		firstname = request.data['firstname']
		lastname = request.data['lastname']
		phone = request.data['phone']
		password = request.data['password']

		if password != "":
			u = Account.objects.get(id=id)
			u.set_password(password)
			u.save()

		Account.objects.filter(id=id).update(
			firstname=firstname, 
			lastname=lastname,
			phone=phone)

		return Response({'success': 'Successfully updated'})

# used - for logout
class LogoutViewAPI(APIView):
	permission_classes = (IsAuthenticated,)
	def post(self, request):
		key = request.data['key']
		Token.objects.filter(key = key).delete()
		return Response({"success": "Successfully logged out."})

# used - for saved job viewing (USER)
class SavedJobUserViewAPI(ListAPIView):
	permission_classes = (IsAuthenticated,)
	queryset = CreateJob.objects.all()
	serializer_class = SavedJobUserSerializer
	lookup_field = 'user_id'

	def get_queryset(self):
		# return SavedJob.objects.raw('SELECT * FROM savedjob, jobofferings, account ' +
		# 	'WHERE account.id = jobofferings.admin_id AND jobofferings.id = savedjob.job_id ' +
		# 	'AND savedjob.user_id = '+self.kwargs['user_id']+' AND jobofferings.is_deleted = 0 ORDER BY savedjob.id DESC')
		return SavedJob.objects.raw('SELECT * FROM "SavedJob", "JobOfferings", "Account" ' +
			'WHERE "Account".id = "JobOfferings".admin_id AND "JobOfferings".id = "SavedJob".job_id ' +
			'AND "SavedJob".user_id = '+self.kwargs['user_id']+' AND "JobOfferings".is_deleted = False ORDER BY "SavedJob".id DESC')

# used - for applied job viewing (USER)
class AppliedJobUserViewAPI(ListAPIView):
	permission_classes = (IsAuthenticated,)
	query = AppliedJob.objects.all()
	serializer_class = AppliedJobSerializer
	lookup_field = 'user_id'

	def get_queryset(self):
		# return AppliedJob.objects.raw('SELECT * FROM appliedjob, jobofferings, account ' +
		# 'WHERE account.id = jobofferings.admin_id AND jobofferings.id = appliedjob.job_id ' +
		# 'AND appliedjob.user_id = '+self.kwargs['user_id']+ ' ORDER BY appliedjob.id DESC')
		return AppliedJob.objects.raw('SELECT * FROM "AppliedJob", "JobOfferings", "Account" ' +
			'WHERE "Account".id = "JobOfferings".admin_id AND "JobOfferings".id = "AppliedJob".job_id ' +
			'AND "AppliedJob".user_id = '+self.kwargs['user_id']+ ' ORDER BY "AppliedJob".id DESC')

# used - for job offerings (USER)
class JobOfferingsViewAPI(ListAPIView):
	permission_classes = (IsAuthenticated,)
	query = CreateJob.objects.all()
	serializer_class = CreateJobSerializer
	lookup_field = 'user_id'

	def get_queryset(self):
		# return CreateJob.objects.raw('SELECT jobofferings.id, jobofferings.title, jobofferings.description, account.email, account.firstname, account.lastname ' +
		# 'FROM jobofferings, account WHERE jobofferings.admin_id = account.id AND jobofferings.id NOT IN ' +
		# '(SELECT savedjob.job_id FROM savedjob WHERE ' + self.kwargs['user_id'] + ' = savedjob.user_id UNION ALL ' +
		# 'SELECT appliedjob.job_id FROM appliedjob WHERE appliedjob.user_id = ' + self.kwargs['user_id'] + ') AND jobofferings.is_deleted=0')
		return CreateJob.objects.raw('SELECT "JobOfferings".id, "JobOfferings".title, "JobOfferings".description, "Account".email, "Account".firstname, "Account".lastname ' +
			'FROM "JobOfferings", "Account" WHERE "JobOfferings".admin_id = "Account".id AND "JobOfferings".id NOT IN ' +
			'(SELECT "SavedJob".job_id FROM "SavedJob" WHERE ' + self.kwargs['user_id'] + ' = "SavedJob".user_id UNION ALL ' +
			'SELECT "AppliedJob".job_id FROM "AppliedJob" WHERE "AppliedJob".user_id = ' + self.kwargs['user_id'] + ') AND "JobOfferings".is_deleted=False')

# used - to SAVE job offering
class SaveJobOfferingCreateViewAPI(CreateAPIView):
	permission_classes = (IsAuthenticated,)
	serializer_class = SavedJobSerializer

# used - to UNSAVE job offering
class UnsaveJobOfferingDestroyView(DestroyAPIView):
	permission_classes = (IsAuthenticated,)
	queryset = SavedJob.objects.all()

class AccountDetailsViewAPI(ListAPIView):
	permission_classes = (AllowAny,)
	queryset = Account.objects.all()
	serializer_class = FewAccountDetailsSerializer

# used - to get the job offerings of an admin
class JobOfferingsAdminListViewAPI(ListAPIView):
	permission_classes = (IsAuthenticated,)
	queryset = CreateJob.objects.all()
	serializer_class = JobOfferingListSerializer
	lookup_field = 'admin_id'

	def get_queryset(self):
		admin_id = self.kwargs['admin_id']
		return CreateJob.objects.filter(admin_id=admin_id,is_deleted=False)

class AppliedJobApplicantsListViewAPI(ListAPIView):
	permission_classes = (IsAuthenticated,)
	query = AppliedJob.objects.all()
	serializer_class = ApplicantViewingSerializer
	lookup_field = 'job_id'

	def get_queryset(self):
		# return AppliedJob.objects.raw('SELECT * FROM account, jobofferings, appliedjob WHERE appliedjob.job_id = ' + self.kwargs['job_id'] +
		# 	' AND appliedjob.job_id = jobofferings.id AND account.id = appliedjob.user_id AND appliedjob.final_score != 0 ORDER BY appliedjob.final_score DESC')
		return AppliedJob.objects.raw('SELECT * FROM "Account", "JobOfferings", "AppliedJob" WHERE "AppliedJob".job_id = ' + self.kwargs['job_id'] +
			' AND "AppliedJob".job_id = "JobOfferings".id AND "Account".id = "AppliedJob".user_id AND "AppliedJob".final_score != 0 ORDER BY "AppliedJob".final_score DESC')

class AppliedJobListViewAPI(ListAPIView):
	permissions = (IsAuthenticated,)
	queryset = AppliedJob.objects.all()
	serializer_class = AppliedJobListSerializer


############################################################################################################
class LoginView(FormView):
	form_class = LoginForm
	template_name = 'log_in.html'

	def form_valid(self, form):
		request = self.request
		_next = request.GET.get('next')
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")
		user = authenticate(request,username=email,password=password)

		if user is not None:
			login(request, user)
			if user.staff or user.admin:
				if _next:
					if 'user' in _next: # if admin wants to access user URLs
						return redirect('administrator:access_denied_view')
					else:
						return redirect(_next)
				else:
					return redirect('administrator:dashboard_view')
			else:
				if _next:
					if 'administrator' in _next: # if user wants to access admin URLs
						return redirect('user:access_denied_view')
					else:
						return redirect(_next)
				else:
					return redirect("user:home_view")
		else:
			messages.error(request,"Email or password is incorrect.")
		return super(LoginView,self).form_invalid(form)

# For password reset feature (Django)
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = Account.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'citu-interviewbot.herokuapp.com',
					'site_name': 'Interview Bot',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'interviewbot.cit@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("password_reset_done")
			else:
				messages.error(request, "Email not registered.")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})
