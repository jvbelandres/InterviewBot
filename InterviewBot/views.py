from django.db.models import query
from django.db.models.query import QuerySet
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
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView

from user.models import Account, CreateJob, SavedJob, AppliedJob
from .serializers import(
	AccountSerializer, 
	JobOfferingListSerializer, 
	JobOfferingDetailedSerializer,
	SavedJobSerializer,
	AppliedJobSerializer
)
from .forms import *

class LoginViewAPI(APIView):
	def post(self, request):
		email = request.data['email']
		password = request.data['password']

		user = authenticate(request, username=email, password=password)

		if user is None:
			raise AuthenticationFailed('Email or password is incorrect')
		else:
			token = Token.objects.create(user=user)
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

class UpdateAccountViewAPI(APIView):
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

					
class LogoutViewAPI(APIView):
	def post(self, request):
		key = request.data['key']
		Token.objects.filter(key = key).delete()
		return Response({"success": "Successfully logged out."})

class AccountDetailsViewAPI(RetrieveAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer
	lookup_field = 'email'

class JobOfferingsListViewAPI(ListAPIView):
	queryset = CreateJob.objects.all()
	serializer_class = JobOfferingListSerializer

class JobOfferingsDetailedViewAPI(RetrieveAPIView):
	queryset = CreateJob.objects.all()
	serializer_class = JobOfferingDetailedSerializer
	lookup_field = 'admin_id'

class SavedJobListViewAPI(ListAPIView):
	queryset = SavedJob.objects.all()
	serializer_class = SavedJobSerializer

class SavedJobDetailedViewAPI(RetrieveAPIView):
	queryset = SavedJob.objects.all()
	serializer_class = SavedJobSerializer
	lookup_field = 'user_id'

class AppliedJobListViewAPI(ListAPIView):
	queryset = AppliedJob.objects.all()
	serializer_class = AppliedJobSerializer

class AppliedJobDetailedUserViewAPI(RetrieveAPIView):
	queryset = SavedJob.objects.all()
	serializer_class = SavedJobSerializer
	lookup_field = 'user_id'

class AppliedJobDetailedAdminViewAPI(RetrieveAPIView):
	queryset = SavedJob.objects.all()
	serializer_class = SavedJobSerializer
	lookup_field = 'job_id'





class LoginView(FormView):
	form_class = LoginForm
	template_name = 'UserLog-inPage.html'

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
					'domain':'127.0.0.1:8000',
					'site_name': 'Interview Bot',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
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