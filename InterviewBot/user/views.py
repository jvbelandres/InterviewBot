from django.http import HttpResponse
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import View, CreateView, FormView

from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.core.paginator import Paginator

from django.utils.datastructures import MultiValueDictKeyError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

import json, requests 

from .forms import *
from .filters import JobSearchFilter
from .tokens import account_activation_token
from user.models import AppliedJob, SavedJob

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

# Text-Processing API
def textProccessing(text):
	url = "https://japerk-text-processing.p.rapidapi.com/sentiment/"
	text = text.replace(" ", "%20") 
	payload = "text="+text+".&language=english"
	headers = {
	    'content-type': "application/x-www-form-urlencoded",
	    'x-rapidapi-key': "bab359c48dmsh0dd3b24fa8d2016p1484e5jsnfabda9701382",
	    'x-rapidapi-host': "japerk-text-processing.p.rapidapi.com"
	}
	response = requests.request("POST", url, data=payload, headers=headers)
	return json.loads(response.text)

# Scoring for each question
def finalScoring(pos, weight):
	return pos * float(weight)

class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = 'RegistrationPage.html'
	
	def form_valid(self, form):
		user = form.save(commit=False)
		user.is_active = False
		pw = form.cleaned_data.get('password')
		user.set_password(pw)
		user.save()
		current_site = get_current_site(self.request)
		mail_subject = 'Activate your account.'
		message = render_to_string('account_activation/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
	    })
		to_email = form.cleaned_data.get('email')
		email = EmailMessage(
					mail_subject, message, to=[to_email]
		)
		email.send()
		self.request.session['email'] = to_email
		return redirect('user:registration_complete')

	def form_invalid(self, form):
		messages.error(self.request, 'Invalid email. Please try another.')
		return super().form_invalid(form)

# Method for account activation
def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64).decode())
		user = Account.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		return redirect('user:activate-success')
	else:
		return redirect('user:activate-failed')

class RegisterComplete(View): # After user registration
	def get(self, request):
		try:
			email = request.session['email']
			return render(request, 'account_activation/register_done.html', {'email': email})
		except:
			return redirect('user:login_view')

class ActivationSuccess(View): # If account activation succeed
	def get(self, request):
		return render(request, 'account_activation/activation_success.html')

class ActivationFailed(View): # If account activation failed
	def get(self, request):
		return render(request, 'account_activation/activation_failed.html')

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

class HomePageView(View):
	def get(self, request):
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		appliedjobs = AppliedJob.objects.raw('SELECT * FROM appliedjob, jobofferings WHERE jobofferings.id = appliedjob.job_id AND appliedjob.user_id = '+str(self.request.user.id))
		savedjobs = SavedJob.objects.raw('SELECT * FROM savedjob, jobofferings WHERE jobofferings.id = savedjob.job_id AND savedjob.user_id = '+str(self.request.user.id))
		context = {
			'appliedjobs': appliedjobs,
			'savedjobs': savedjobs
		}
		return render(request, 'homePage.html', context)

	def post(self, request):
		if request.method == "POST":
			if 'btnUnsave' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				savedjobs = SavedJob.objects.filter(job_id = job_id).delete()
				return redirect('user:home_view')
			elif 'btnApply' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				request.session['job'] = job_id
				savedjobs = SavedJob.objects.filter(job_id = job_id).delete()

				# To store the files in the media dir
				fs = FileSystemStorage();

				try:
					r1 = request.FILES['myfile1']
					resume = user.lastname+"_"+user.firstname+"_resume.pdf"
					file_name = fs.save(resume, r1)
				except MultiValueDictKeyError:
					file_name = None

				apply_job = AppliedJob(requirement_1 = file_name, job_id = job_id, user_id = user.id)
				apply_job.save()

				request.session['q1'] = False
				request.session['q2'] = False
				request.session['q3'] = False
				request.session['q4'] = False
				request.session['q5'] = False
				request.session['q6'] = False
				request.session['q7'] = False
				request.session['q8'] = False
				request.session['q9'] = False
				request.session['q10'] = False
				request.session['q11'] = False
				request.session['q12'] = False
				request.session['q13'] = False
				request.session['q14'] = False
				request.session['q15'] = False
				request.session['q16'] = False
				request.session['q17'] = False
				request.session['q18'] = False
				request.session['q19'] = False
				request.session['q20'] = False
				
				return redirect('user:job-interview_view')

class LogOutView(View):
	def get(self, request):
		logout(request)
		return render(request, 'Logout.html')

class AboutUsView(View):
	def get(self, request):
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'AboutUs.html')

class ContactUsView(View):
	def get(self, request):
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'ContactUs.html')

	def post(self, request):
		form = ContactForm(request.POST)
		user = request.user

		if form.is_valid():
			subject = request.POST.get("subject")
			message = request.POST.get("message")
			form = Contact(email = user.email, subject = subject, message = message)
			form.save()

			send_mail(subject,message,user.email,['interviewbot.cit@gmail.com'])
			return redirect('user:mailsent_view')

		return render(request, 'ContactUs.html')

class MailSentView(View):
	def get(self,request):
		return render(request, 'MailSent.html')

class AccessDeniedView(View):
	def get(self, request):
		return render(request, 'accessDenied.html')

class JobOffersView(View):
	def get(self, request):
		user = request.user
		if user.staff:
			return redirect('administrator:access_denied_view')
		joblists = CreateJob.objects.raw('SELECT jobofferings.id, jobofferings.title, jobofferings.description FROM jobofferings WHERE jobofferings.id NOT IN (SELECT savedjob.job_id FROM savedjob WHERE '+str(user.id)+' = savedjob.user_id UNION ALL SELECT appliedjob.job_id FROM appliedjob WHERE appliedjob.user_id = '+str(user.id)+') AND jobofferings.is_deleted=0')
		saved_jobs = SavedJob.objects.filter(user_id = user.id)

		joblists = CreateJob.objects.all()
		joblist_filter = JobSearchFilter(request.GET, queryset = joblists)

		p = Paginator(joblist_filter.qs, 4)
		page_number = request.GET.get('page',1)
		page = p.page(page_number)
		numberOfPage = p.num_pages
        
		array = []
		for x in range(1, numberOfPage+1):
			array.append(x)

		context = {
			'joblists': page,
			'pages':array,
			'page_number':int(page_number),
			'saved_jobs': saved_jobs,
			'joblist_filter': joblist_filter,
		}
		return render(request, 'jobOffers.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnSave' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")

				save_jobs = SavedJob.objects.create(job_id = job_id, user_id = user.id)

				return redirect('user:job-offers_view')
			elif 'btnApply' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				request.session['job'] = job_id
				savedjobs = SavedJob.objects.filter(job_id = job_id).delete()

				# To store the files in the media dir
				fs = FileSystemStorage();

				try:
					r1 = request.FILES['myfile1']
					resume = user.lastname+"_"+user.firstname+"_resume.pdf"
					file_name = fs.save(resume, r1)
				except MultiValueDictKeyError:
					file_name = None

				apply_job = AppliedJob(requirement_1 = file_name, job_id = job_id, user_id = user.id)
				apply_job.save()

				request.session['q1'] = False
				request.session['q2'] = False
				request.session['q3'] = False
				request.session['q4'] = False
				request.session['q5'] = False
				request.session['q6'] = False
				request.session['q7'] = False
				request.session['q8'] = False
				request.session['q9'] = False
				request.session['q10'] = False
				request.session['q11'] = False
				request.session['q12'] = False
				request.session['q13'] = False
				request.session['q14'] = False
				request.session['q15'] = False
				request.session['q16'] = False
				request.session['q17'] = False
				request.session['q18'] = False
				request.session['q19'] = False
				request.session['q20'] = False

				return redirect('user:job-interview_view')

class SettingsView(FormView):
	def get(self, request):
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'Settings.html')

	def post(self, request):
		user = request.user
		firstName = request.POST.get("firstname")
		lastName = request.POST.get("lastname")
		phone = request.POST.get("phone")
		password = request.POST.get("password")

		if password == "":
			update_account = Account.objects.filter(id = user.id).update(firstname = firstName, 
				lastname = lastName, phone = phone)
		else:
			u = Account.objects.get(email=user.email)
			u.set_password(password)
			u.save()
			# relogin since after saving, the user is logged-out
			loginUser = authenticate(request,username=user.email,password=password)
			login(request,loginUser)
			update_account = Account.objects.filter(id = u.id).update(firstname = firstName, 
				lastname = lastName, phone = phone)

		return redirect('user:settings_view')

class JobInterviewView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')
			interview_job = request.session['job']
			job = CreateJob.objects.filter(id = interview_job)
			context = {
				'job': job
			}
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'jobOffer_Interview.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnCancel' in request.POST:
				interview_job = request.session['job']
				delete_requirement = AppliedJob.objects.filter(job_id = interview_job).delete()
				return redirect('user:job-offers_view')

class JobInterviewQ1View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q1'] == False:
				request.session['q1'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q1.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_1 = request.POST.get("message")
		
		if len(response_1) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_1)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_1 = response_1, positive1 = positive, score1 = final_score)
		return redirect('user:job-interview_q2')

class JobInterviewQ2View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q2'] == False:
				request.session['q2'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q2.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_2 = request.POST.get("message")
		
		if len(response_2) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_2)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_2 = response_2, positive2 = positive, score2 = final_score)
		return redirect('user:job-interview_q3')

class JobInterviewQ3View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q3'] == False:
				request.session['q3'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')	
		return render(request, 'questions/jobInterview_Q3.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_3 = request.POST.get("message")

		if len(response_3) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_3)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_3 = response_3, positive3 = positive, score3 = final_score)
		return redirect('user:job-interview_q4')

class JobInterviewQ4View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q4'] == False:
				request.session['q4'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q4.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_4 = request.POST.get("message")

		if len(response_4) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_4)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_4 = response_4, positive4 = positive, score4 = final_score)
		return redirect('user:job-interview_q5')

class JobInterviewQ5View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q5'] == False:
				request.session['q5'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q5.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_5 = request.POST.get("message")
		
		if len(response_5) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_5)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_5 = response_5, positive5 = positive, score5 = final_score)
		return redirect('user:job-interview_q6')

class JobInterviewQ6View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q6'] == False:
				request.session['q6'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q6.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_6 = request.POST.get("message")

		if len(response_6) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_6)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_6 = response_6, positive6 = positive, score6 = final_score)
		return redirect('user:job-interview_q7')

class JobInterviewQ7View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q7'] == False:
				request.session['q7'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q7.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_7 = request.POST.get("message")

		if len(response_7) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_7)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_7 = response_7, positive7 = positive, score7 = final_score)
		return redirect('user:job-interview_q8')

class JobInterviewQ8View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q8'] == False:
				request.session['q8'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q8.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_8 = request.POST.get("message")

		if len(response_8) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_8)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_8 = response_8, positive8 = positive, score8 = final_score)
		return redirect('user:job-interview_q9')

class JobInterviewQ9View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q9'] == False:
				request.session['q9'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q9.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_9 = request.POST.get("message")

		if len(response_9) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_9)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_9 = response_9, positive9 = positive, score9 = final_score)
		return redirect('user:job-interview_q10')

class JobInterviewQ10View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q10'] == False:
				request.session['q10'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q10.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_10 = request.POST.get("message")

		if len(response_10) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_10)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_10 = response_10, positive10 = positive, score10 = final_score)
		return redirect('user:job-interview_q11')

class JobInterviewQ11View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q11'] == False:
				request.session['q11'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q11.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_11 = request.POST.get("message")

		if len(response_11) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_11)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_11 = response_11, positive11 = positive, score11 = final_score)
		return redirect('user:job-interview_q12')

class JobInterviewQ12View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q12'] == False:
				request.session['q12'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q12.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_12 = request.POST.get("message")

		if len(response_12) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_12)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_12 = response_12, positive12 = positive, score12 = final_score)
		return redirect('user:job-interview_q13')

class JobInterviewQ13View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q13'] == False:
				request.session['q13'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q13.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_13 = request.POST.get("message")

		if len(response_13) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_13)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_13 = response_13, positive13 = positive, score13 = final_score)
		return redirect('user:job-interview_q14')

class JobInterviewQ14View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q14'] == False:
				request.session['q14'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q14.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_14 = request.POST.get("message")

		if len(response_14) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_14)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_14 = response_14, positive14 = positive, score14 = final_score)
		return redirect('user:job-interview_q15')

class JobInterviewQ15View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q15'] == False:
				request.session['q15'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q15.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_15 = request.POST.get("message")

		if len(response_15) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_15)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_15 = response_15, positive15 = positive, score15 = final_score)
		return redirect('user:job-interview_q16')

class JobInterviewQ16View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q16'] == False:
				request.session['q16'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q16.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_16 = request.POST.get("message")

		if len(response_16) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_16)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_16 = response_16, positive16 = positive, score16 = final_score)
		return redirect('user:job-interview_q17')

class JobInterviewQ17View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q17'] == False:
				request.session['q17'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q17.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_17 = request.POST.get("message")
		
		if len(response_17) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_17)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_17 = response_17, positive17 = positive, score17 = final_score)
		return redirect('user:job-interview_q18')

class JobInterviewQ18View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q18'] == False:
				request.session['q18'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q18.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_18 = request.POST.get("message")

		if len(response_18) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_18)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_18 = response_18, positive18 = positive, score18 = final_score)
		return redirect('user:job-interview_q19')

class JobInterviewQ19View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q19'] == False:
				request.session['q19'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q19.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_19 = request.POST.get("message")

		if len(response_19) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_19)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_19 = response_19, positive19 = positive, score19 = final_score)
		return redirect('user:job-interview_q20')

class JobInterviewQ20View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q20'] == False:
				request.session['q20'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'questions/jobInterview_Q20.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight1 = request.POST.get("job-weight1")
		job_weight2 = request.POST.get("job-weight2")
		job_weight3 = request.POST.get("job-weight3")
		job_weight4 = request.POST.get("job-weight4")
		job_weight5 = request.POST.get("job-weight5")
		job_weight6 = request.POST.get("job-weight6")
		job_weight7 = request.POST.get("job-weight7")
		job_weight8 = request.POST.get("job-weight8")
		job_weight9 = request.POST.get("job-weight9")
		job_weight10 = request.POST.get("job-weight10")
		response_20 = request.POST.get("message")

		if len(response_20) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_20)

			# getting the positive score
			dict_response = json_object.get('probability')
			positive = dict_response.get('pos')
		else:
			positive = 0

		# get final score (question 20)
		score20 = finalScoring(positive, job_weight10)

		# get final score for the overall interview session
		u = AppliedJob.objects.filter(job_id = job_id, user_id = user.id)
		for u in u:
			if u.score1 != None or u.score2 != None or u.score3 != None or u.score4 != None or u.score5 != None or u.score6 != None or u.score7 != None or u.score8 != None or u.score9 != None or u.score10 != None or u.score11 != None or u.score12 != None or u.score13 != None or u.score14 != None or u.score15 != None or u.score16 != None or u.score17 != None or u.score18 != None or u.score19 != None or u.score20 != None:
				final_score = ((u.score1 + u.score2 + u.score3 + u.score4 + u.score5 + u.score6 +
					u.score7 + u.score8 + u.score9 + u.score10 + u.score11 + u.score12 + u.score13 +
					u.score14 + u.score15 + u.score15 + u.score16 + u.score17 + u.score18 + u.score19 +
					score20) / (10 + float(job_weight1) + float(job_weight2) + float(job_weight3) + 
					float(job_weight4) + float(job_weight5) +float(job_weight6) + float(job_weight7) + 
					float(job_weight8) + float(job_weight9) + float(job_weight10)))
				final_score_decimal = round(final_score, 4)
				final_score_percent = final_score_decimal * 100
			else:
				# if one question was not answered
				update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
					response_20 = response_20, positive20 = positive, score20 = score20, final_score = 0)
				return redirect('user:interview_forfeit_view')

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_20 = response_20, positive20 = positive, score20 = score20, final_score = final_score_percent)

		return redirect('user:interview_success_view')

class InterviewSuccessView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			del request.session['job']
			del request.session['q1']
			del request.session['q2']
			del request.session['q3']
			del request.session['q4']
			del request.session['q5']
			del request.session['q6']
			del request.session['q7']
			del request.session['q8']
			del request.session['q9']
			del request.session['q10']
			del request.session['q11']
			del request.session['q12']
			del request.session['q13']
			del request.session['q14']
			del request.session['q15']
			del request.session['q16']
			del request.session['q17']
			del request.session['q18']
			del request.session['q19']
			del request.session['q20']
		except KeyError:
			return redirect('user:interview_access_denied')
		except: 
			pass
		return render(request, 'interviewSuccess.html')

class InterviewForfeitView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')
		except KeyError:
			return redirect('user:interview_access_denied')
		return render(request, 'interviewForfeit.html')

class JobInterviewAccessDenied(View):
	def get(self, request):
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'jobInterviewAccessDenied.html')