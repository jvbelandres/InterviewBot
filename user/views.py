from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import View, CreateView, FormView

from django.core.mail import send_mail, EmailMessage

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site

import json, requests, math

from .forms import *
from .tokens import account_activation_token
from user.models import AppliedJob, SavedJob

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
def finalScoring(initScore, weight, minutes, seconds, timer):
	if initScore != 0:
		seconds_remaining = (minutes * 60) + seconds
		total_seconds_timer = timer * 60
		add_points_timer = 0

		if float(seconds_remaining) >= (float(total_seconds_timer) * .8):
			add_points_timer = 0.20
		elif float(seconds_remaining) < (float(total_seconds_timer) * .8) and float(seconds_remaining) >= (float(total_seconds_timer) * .6):
			add_points_timer = 0.15
		elif float(seconds_remaining) < (float(total_seconds_timer) * .6) and float(seconds_remaining) >= (float(total_seconds_timer) * .4):
			add_points_timer = 0.10
		elif float(seconds_remaining) < (float(total_seconds_timer) * .4) and float(seconds_remaining) >= (float(total_seconds_timer) * .2):
			add_points_timer = 0.05
		else:
			add_points_timer = 0

		return (round(initScore, 2) * float(weight) + float(add_points_timer)) * 100
	else:
		return 0

# Scoring for sentiment score
def calculateSentimentScore(positive, negative, neutral):
	if (positive == 0 or negative == 0 or neutral == 0):
		return 0
	return round((positive * 0.7) + (neutral * 0.2) + (negative * 0.1), 2)
	#return round((positive * 0.6) + (neutral * 0.3) + (negative * 0.1), 2)

# Delete sessions if user skip or did not continue the job interview session
def deleteInterviewSessions(request):
	# in case user will skip or not continue the job interview session
	try:
		if request.session['instruction'] and not request.session['q1']:
			AppliedJob.objects.filter(job_id=request.session['job'], user_id=request.user.id).delete()
		elif not request.session['instruction']:
			AppliedJob.objects.filter(job_id = request.session['job'], user_id = request.user.id).update(final_score = 0)

			del request.session['job']
			del request.session['instruction']
			del request.session['on-interview']
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
			
			return redirect('user:interview_forfeit_view')	
	except:
		pass

class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = 'registration_page.html'
	
	def form_valid(self, form):
		user = form.save(commit=False)
		user.is_active = False
		pw = form.cleaned_data.get('password')
		user.set_password(pw)
		user.save()
		current_site = get_current_site(self.request)
		mail_subject = 'Activate your account.'
		message = render_to_string('account_activation/user/acc_active_email.html', {
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
		json_error = form.errors.as_json()
		phoneError = "phone" in json_error
		if phoneError:
			messages.warning(self.request, form.errors['phone'])
		else:
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
			return render(request, 'account_activation/user/register_done.html', {'email': email})
		except:
			return redirect('login_view')

class ActivationSuccess(View): # If account activation succeed
	def get(self, request):
		return render(request, 'account_activation/user/activation_success.html')

class ActivationFailed(View): # If account activation failed
	def get(self, request):
		return render(request, 'account_activation/user/activation_failed.html')

class HomePageView(View):
	def get(self, request):
		deleteInterviewSessions(request)

		if request.user.staff:
			return redirect('administrator:access_denied_view')
		
		try: # To only show the applied jobs that are done taking the interview session.
			#appliedjobs = AppliedJob.objects.raw('SELECT * FROM appliedjob, jobofferings, account WHERE account.id = jobofferings.admin_id AND jobofferings.id = appliedjob.job_id AND appliedjob.job_id <> '+str(request.session['job'])+' AND appliedjob.user_id = '+str(self.request.user.id)+' ORDER BY appliedjob.id DESC')
			appliedjobs = AppliedJob.objects.raw('SELECT * FROM "AppliedJob", "JobOfferings", "Account" WHERE "Account".id = "JobOfferings".admin_id AND "JobOfferings".id = "AppliedJob".job_id AND "AppliedJob".job_id <> '+str(request.session['job'])+' AND "AppliedJob".user_id = '+str(self.request.user.id)+' ORDER BY "AppliedJob".id DESC')
		except:
			#appliedjobs = AppliedJob.objects.raw('SELECT * FROM appliedjob, jobofferings, account WHERE account.id = jobofferings.admin_id AND jobofferings.id = appliedjob.job_id AND appliedjob.user_id = '+str(self.request.user.id)+' ORDER BY appliedjob.id DESC')
			appliedjobs = AppliedJob.objects.raw('SELECT * FROM "AppliedJob", "JobOfferings", "Account" WHERE "Account".id = "JobOfferings".admin_id AND "JobOfferings".id = "AppliedJob".job_id AND "AppliedJob".user_id = '+str(self.request.user.id)+' ORDER BY "AppliedJob".id DESC')
		
		#savedjobs = SavedJob.objects.raw('SELECT * FROM savedjob, jobofferings, account WHERE account.id = jobofferings.admin_id AND jobofferings.id = savedjob.job_id AND savedjob.user_id = '+str(self.request.user.id)+' ORDER BY savedjob.id DESC')
		savedjobs = SavedJob.objects.raw('SELECT * FROM "SavedJob", "JobOfferings", "Account" WHERE "Account".id = "JobOfferings".admin_id AND "JobOfferings".id = "SavedJob".job_id AND "SavedJob".user_id = '+str(self.request.user.id)+' ORDER BY "SavedJob".id DESC')
		context = {
			'appliedjobs': appliedjobs,
			'savedjobs': savedjobs
		}
		return render(request, 'home_page.html', context)

	def post(self, request):
		if request.method == "POST":
			if 'btnUnsave' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				SavedJob.objects.filter(job_id = job_id).delete()
				return redirect('user:home_view')
			elif 'btnApply' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				request.session['job'] = job_id
				SavedJob.objects.filter(job_id = job_id).delete()

				apply_job = AppliedJob(job_id = job_id, user_id = user.id)
				apply_job.save()

				request.session['instruction'] = False
				request.session['on-interview'] = False
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
		deleteInterviewSessions(request)
		logout(request)
		return render(request, 'log_out.html')

class AboutUsView(View):
	def get(self, request):
		deleteInterviewSessions(request)
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'about_us.html')

class ContactUsView(View):
	def get(self, request):
		deleteInterviewSessions(request)
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'contact_us.html')

	def post(self, request):
		form = ContactForm(request.POST)
		user = request.user

		if form.is_valid():
			subject = request.POST.get("subject")
			message = request.POST.get("message")
			form = Contact(email = user.email, subject = subject, message = message)
			form.save()

			send_mail(subject,message,user.email,['interviewbot.cit@gmail.com'])
			messages.success(request, 'sent')
			return redirect('user:contact-us_view')

		return render(request, 'contact_us.html')

class AccessDeniedView(View):
	def get(self, request):
		return render(request, 'access_denied.html')

class JobOffersView(View):
	def get(self, request):
		deleteInterviewSessions(request)
		user = request.user
		if user.staff:
			return redirect('administrator:access_denied_view')
		
		saved_jobs = SavedJob.objects.filter(user_id = user.id)
		#joblists = CreateJob.objects.raw('SELECT jobofferings.id, jobofferings.title, jobofferings.description, account.email, account.firstname, account.lastname FROM jobofferings, account WHERE jobofferings.admin_id = account.id AND jobofferings.id NOT IN (SELECT savedjob.job_id FROM savedjob WHERE '+str(user.id)+' = savedjob.user_id UNION ALL SELECT appliedjob.job_id FROM appliedjob WHERE appliedjob.user_id = '+str(user.id)+') AND jobofferings.is_deleted=0')
		joblists = CreateJob.objects.raw('SELECT "JobOfferings".id, "JobOfferings".title, "JobOfferings".description, "Account".email, "Account".firstname, "Account".lastname FROM "JobOfferings", "Account" WHERE "JobOfferings".admin_id = "Account".id AND "JobOfferings".id NOT IN (SELECT "SavedJob".job_id FROM "SavedJob" WHERE '+str(user.id)+' = "SavedJob".user_id UNION ALL SELECT "AppliedJob".job_id FROM "AppliedJob" WHERE "AppliedJob".user_id = '+str(user.id)+') AND "JobOfferings".is_deleted=False')

		context = {
			'joblists': joblists,
			'saved_jobs': saved_jobs,
		}
		return render(request, 'job_offers.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnSave' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")

				SavedJob.objects.create(job_id = job_id, user_id = user.id)

				return redirect('user:job-offers_view')
			elif 'btnApply' in request.POST:
				user = request.user
				job_id = request.POST.get("job-id")
				request.session['job'] = job_id
				SavedJob.objects.filter(job_id = job_id).delete()

				apply_job = AppliedJob(job_id = job_id, user_id = user.id)
				apply_job.save()

				request.session['instruction'] = False
				request.session['on-interview'] = False
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
		deleteInterviewSessions(request)
		if request.user.staff:
			return redirect('administrator:access_denied_view')
		return render(request, 'user_settings.html')

	def post(self, request):
		user = request.user
		firstName = request.POST.get("firstname")
		lastName = request.POST.get("lastname")
		phone = request.POST.get("phone")
		password = request.POST.get("password")

		if password == "":
			Account.objects.filter(id = user.id).update(firstname = firstName, 
				lastname = lastName, phone = phone)
		else:
			u = Account.objects.get(email=user.email)
			u.set_password(password)
			u.save()
			# relogin since after saving, the user is logged-out
			loginUser = authenticate(request,username=user.email,password=password)
			login(request,loginUser)
			Account.objects.filter(id = u.id).update(firstname = firstName, 
				lastname = lastName, phone = phone)
		messages.success(request, 'updated')
		return redirect('user:settings_view')

class JobInterviewView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['instruction'] == False:
				request.session['instruction'] = True
				interview_job = request.session['job']
				job = CreateJob.objects.filter(id = interview_job)
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'interview_instructions.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnCancel' in request.POST:
				interview_job = request.session['job']
				try:
					del request.session['job']
					del request.session['instruction']
					del request.session['on-interview']
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
				except:
					pass
				AppliedJob.objects.filter(job_id = interview_job).delete()
				return redirect('user:job-offers_view')
			elif 'btnProceed' in request.POST:
				request.session['on-interview'] = True
				return redirect('user:job-interview_q1')

class JobInterviewQ1View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q1'] == False:
				request.session['q1'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q1.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_1 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")
			
			if len(response_1) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_1)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_1 = response_1, score1 = math.ceil(final_score))
			return redirect('user:job-interview_q2')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ2View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q2'] == False:
				request.session['q2'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q2.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_2 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")
			
			if len(response_2) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_2)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_2 = response_2, score2 = math.ceil(final_score))
			return redirect('user:job-interview_q3')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ3View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q3'] == False:
				request.session['q3'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')	
		return render(request, 'questions/jobInterview_Q3.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_3 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_3) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_3)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_3 = response_3, score3 = math.ceil(final_score))
			return redirect('user:job-interview_q4')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ4View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q4'] == False:
				request.session['q4'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q4.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_4 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_4) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_4)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_4 = response_4, score4 = math.ceil(final_score))
			return redirect('user:job-interview_q5')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ5View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q5'] == False:
				request.session['q5'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q5.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_5 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")
			
			if len(response_5) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_5)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_5 = response_5, score5 = math.ceil(final_score))
			return redirect('user:job-interview_q6')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ6View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q6'] == False:
				request.session['q6'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q6.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_6 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_6) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_6)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_6 = response_6, score6 = math.ceil(final_score))
			return redirect('user:job-interview_q7')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ7View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q7'] == False:
				request.session['q7'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q7.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_7 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_7) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_7)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_7 = response_7, score7 = math.ceil(final_score))
			return redirect('user:job-interview_q8')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ8View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q8'] == False:
				request.session['q8'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q8.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_8 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_8) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_8)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_8 = response_8, score8 = math.ceil(final_score))
			return redirect('user:job-interview_q9')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ9View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q9'] == False:
				request.session['q9'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q9.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_9 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_9) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_9)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_9 = response_9, score9 = math.ceil(final_score))
			return redirect('user:job-interview_q10')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ10View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q10'] == False:
				request.session['q10'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q10.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_10 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_10) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_10)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_10 = response_10, score10 = math.ceil(final_score))
			return redirect('user:job-interview_q11')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ11View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q11'] == False:
				request.session['q11'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q11.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_11 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_11) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_11)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_11 = response_11, score11 = math.ceil(final_score))
			return redirect('user:job-interview_q12')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ12View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q12'] == False:
				request.session['q12'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q12.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_12 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_12) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_12)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_12 = response_12, score12 = math.ceil(final_score))
			return redirect('user:job-interview_q13')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ13View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q13'] == False:
				request.session['q13'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q13.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_13 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_13) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_13)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_13 = response_13, score13 = math.ceil(final_score))
			return redirect('user:job-interview_q14')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ14View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q14'] == False:
				request.session['q14'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q14.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_14 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_14) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_14)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_14 = response_14, score14 = math.ceil(final_score))
			return redirect('user:job-interview_q15')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ15View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q15'] == False:
				request.session['q15'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q15.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_15 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_15) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_15)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_15 = response_15, score15 = math.ceil(final_score))
			return redirect('user:job-interview_q16')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ16View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q16'] == False:
				request.session['q16'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q16.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_16 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_16) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_16)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_16 = response_16, score16 = math.ceil(final_score))
			return redirect('user:job-interview_q17')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ17View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q17'] == False:
				request.session['q17'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q17.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_17 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")
			
			if len(response_17) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_17)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_17 = response_17, score17 = math.ceil(final_score))
			return redirect('user:job-interview_q18')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ18View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q18'] == False:
				request.session['q18'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q18.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_18 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_18) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_18)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_18 = response_18, score18 = math.ceil(final_score))
			return redirect('user:job-interview_q19')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ19View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q19'] == False:
				request.session['q19'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q19.html', context)

	def post(self, request):
		try:
			user = request.user
			job_id = request.session['job']
			job_weight = request.POST.get("job-weight")
			job_timer = request.POST.get("job-timer")
			response_19 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_19) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_19)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			final_score = finalScoring(sentimentScore, job_weight, float(minutes), float(seconds), job_timer)

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_19 = response_19, score19 = math.ceil(final_score))
			return redirect('user:job-interview_q20')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class JobInterviewQ20View(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			if request.session['q20'] == False:
				request.session['q20'] = True
				interview_job = request.session['job']
				#job = CreateJob.objects.raw("SELECT * FROM jobofferings, job_questions WHERE jobofferings.id = job_questions.job_id AND jobofferings.id = " + str(interview_job))
				job = CreateJob.objects.raw('SELECT * FROM "JobOfferings", "job_questions" WHERE "JobOfferings".id = "job_questions".job_id AND "JobOfferings".id = ' + str(interview_job))
				context = {
					'job': job
				}
			else:
				return redirect('user:interview_forfeit_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')
		return render(request, 'questions/jobInterview_Q20.html', context)

	def post(self, request):
		try:
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
			job_weight11 = request.POST.get("job-weight11")
			job_weight12 = request.POST.get("job-weight12")
			job_weight13 = request.POST.get("job-weight13")
			job_weight14 = request.POST.get("job-weight14")
			job_weight15 = request.POST.get("job-weight15")
			job_weight16 = request.POST.get("job-weight16")
			job_weight17 = request.POST.get("job-weight17")
			job_weight18 = request.POST.get("job-weight18")
			job_weight19 = request.POST.get("job-weight19")
			job_weight20 = request.POST.get("job-weight20")
			job_timer = request.POST.get("job-timer")
			response_20 = request.POST.get("message")
			minutes = request.POST.get("minutes")
			seconds = request.POST.get("seconds")

			if len(response_20) > 0:
				# use Text-Proccessing API
				json_object = textProccessing(response_20)

				# getting the sentiment scores
				dict_response = json_object.get('probability')
				positive = dict_response.get('pos')
				negative = dict_response.get('neg')
				neutral = dict_response.get('neutral')
			else:
				positive = 0
				negative = 0
				neutral = 0

			sentimentScore = calculateSentimentScore(positive, negative, neutral)

			# Calculate the final score
			score20 = finalScoring(sentimentScore, job_weight20, float(minutes), float(seconds), job_timer)

			# get final score for the overall interview session
			user_appliedJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id)
			for u in user_appliedJob:
				print(u.score1)
				print(u.score2)
				print(u.score3)
				print(u.score4)
				print(u.score5)
				print(u.score6)
				print(u.score7)
				print(u.score8)
				print(u.score9)
				print(u.score10)
				print(u.score11)
				print(u.score12)
				print(u.score13)
				print(u.score14)
				print(u.score15)
				print(u.score16)
				print(u.score17)
				print(u.score18)
				print(u.score19)
				print(score20)


				if u.score1 != None and u.score2 != None and u.score3 != None and u.score4 != None and u.score5 != None and u.score6 != None and u.score7 != None and u.score8 != None and u.score9 != None and u.score10 != None and u.score11 != None and u.score12 != None and u.score13 != None and u.score14 != None and u.score15 != None and u.score16 != None and u.score17 != None and u.score18 != None and u.score19 != None and score20 != 0:	
					final_score = (
						(float(u.score1) * float(job_weight1)) + 
						(float(u.score2) * float(job_weight2)) +
						(float(u.score3) * float(job_weight3)) +
						(float(u.score4) * float(job_weight4)) +
						(float(u.score5) * float(job_weight5)) +
						(float(u.score6) * float(job_weight6)) +
						(float(u.score7) * float(job_weight7)) +
						(float(u.score8) * float(job_weight8)) +
						(float(u.score9) * float(job_weight9)) +
						(float(u.score10) * float(job_weight10)) +
						(float(u.score11) * float(job_weight11)) +
						(float(u.score12) * float(job_weight12)) +
						(float(u.score13) * float(job_weight13)) +
						(float(u.score14) * float(job_weight14)) +
						(float(u.score15) * float(job_weight15)) +
						(float(u.score16) * float(job_weight16)) +
						(float(u.score17) * float(job_weight17)) +
						(float(u.score18) * float(job_weight18)) +
						(float(u.score19) * float(job_weight19)) +
						(float(score20) * float(job_weight20))) / (
						float(job_weight1) + 
						float(job_weight2) + 
						float(job_weight3) + 
						float(job_weight4) + 
						float(job_weight5) + 
						float(job_weight6) + 
						float(job_weight7) + 
						float(job_weight8) + 
						float(job_weight9) + 
						float(job_weight10) + 
						float(job_weight11) + 
						float(job_weight12) + 
						float(job_weight13) + 
						float(job_weight14) + 
						float(job_weight15) + 
						float(job_weight16) + 
						float(job_weight17) + 
						float(job_weight18) + 
						float(job_weight19) + 
						float(job_weight20))
					break
				else:
					# if one score is null
					AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
						response_20 = response_20, score20 = score20, final_score = 0)
					return redirect('user:interview_forfeit_view')

			AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
				response_20 = response_20, score20 = math.ceil(score20), final_score = final_score)

			return redirect('user:interview_success_view')
		except KeyError:
			return redirect('user:interview_forfeit_view')

class InterviewSuccessView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			del request.session['job']
			del request.session['instruction']
			del request.session['on-interview']
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
			return redirect('user:interview_forfeit_view')
		except: 
			pass
		return render(request, 'interview_success.html')

class InterviewForfeitView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

			AppliedJob.objects.filter(job_id = request.session['job'], user_id = request.user.id).update(final_score = 0)

			del request.session['job']
			del request.session['instruction']
			del request.session['on-interview']
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
			pass
		return render(request, 'interview_forfeit.html')