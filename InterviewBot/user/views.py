from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.utils.datastructures import MultiValueDictKeyError

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

# import nltk
# nltk.download('vader_lexicon')
# import string
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

import json
import requests

from .forms import *
from user.models import AppliedJob, SavedJob

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

def finalScoring(pos, weight):
	return pos * float(weight)

class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = 'RegistrationPage.html'
	success_url = '/user/login/'

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
		joblists = CreateJob.objects.raw('SELECT jobofferings.id, jobofferings.title, jobofferings.description FROM jobofferings WHERE jobofferings.id NOT IN (SELECT savedjob.job_id FROM savedjob WHERE '+str(user.id)+' = savedjob.user_id UNION ALL SELECT appliedjob.job_id FROM appliedjob WHERE appliedjob.user_id = '+str(user.id)+')')
		saved_jobs = SavedJob.objects.filter(user_id = user.id)
		context = {
			'joblists': joblists,
			'saved_jobs': saved_jobs
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
		return render(request, 'jobInterview_Q1.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_1 = request.POST.get("message")
		
		if len(response_1) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_1)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_1 = response_1, positive1 = positive, negative1 = negative, neutral1 = neutral, 
			label1 = label, score1 = final_score)
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
		return render(request, 'jobInterview_Q2.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_2 = request.POST.get("message")
		
		if len(response_2) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_2)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_2 = response_2, positive2 = positive, negative2 = negative, neutral2 = neutral, 
			label2 = label, score2 = final_score)
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
		return render(request, 'jobInterview_Q3.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_3 = request.POST.get("message")

		if len(response_3) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_3)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_3 = response_3, positive3 = positive, negative3 = negative, neutral3 = neutral, 
			label3 = label, score3 = final_score)
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
		return render(request, 'jobInterview_Q4.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_4 = request.POST.get("message")

		if len(response_4) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_4)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_4 = response_4, positive4 = positive, negative4 = negative, neutral4 = neutral, 
			label4 = label, score4 = final_score)
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
		return render(request, 'jobInterview_Q5.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_5 = request.POST.get("message")
		
		if len(response_5) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_5)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')

			# Score multiplied by weight
			final_score = finalScoring(positive, 1)
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_5 = response_5, positive5 = positive, negative5 = negative, neutral5 = neutral, 
			label5 = label, score5 = final_score)
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
		return render(request, 'jobInterview_Q6.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_6 = request.POST.get("message")

		if len(response_6) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_6)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_6 = response_6, positive6 = positive, negative6 = negative, neutral6 = neutral, 
			label6 = label, score6 = final_score)
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
		return render(request, 'jobInterview_Q7.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_7 = request.POST.get("message")

		if len(response_7) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_7)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_7 = response_7, positive7 = positive, negative7 = negative, neutral7 = neutral, 
			label7 = label, score7 = final_score)
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
		return render(request, 'jobInterview_Q8.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_8 = request.POST.get("message")

		if len(response_8) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_8)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_8 = response_8, positive8 = positive, negative8 = negative, neutral8 = neutral, 
			label8 = label, score8 = final_score)
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
		return render(request, 'jobInterview_Q9.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_9 = request.POST.get("message")

		if len(response_9) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_9)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_9 = response_9, positive9 = positive, negative9 = negative, neutral9 = neutral, 
			label9 = label, score9 = final_score)
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
		return render(request, 'jobInterview_Q10.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		response_10 = request.POST.get("message")

		if len(response_10) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_10)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# Score multiplied by weight
		final_score = finalScoring(positive, 1)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_10 = response_10, positive10 = positive, negative10 = negative, neutral10 = neutral, 
			label10 = label, score10 = final_score)
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
		return render(request, 'jobInterview_Q11.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_11 = request.POST.get("message")

		if len(response_11) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_11)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_11 = response_11, label11 = label, positive11 = positive, negative11 = negative, 
			neutral11 = neutral, score11 = final_score)
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
		return render(request, 'jobInterview_Q12.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_12 = request.POST.get("message")

		if len(response_12) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_12)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_12 = response_12, label12 = label, positive12 = positive, negative12 = negative, 
			neutral12 = neutral, score12 = final_score)
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
		return render(request, 'jobInterview_Q13.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_13 = request.POST.get("message")

		if len(response_13) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_13)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_13 = response_13, label13 = label, positive13 = positive, negative13 = negative, 
			neutral13 = neutral, score13 = final_score)
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
		return render(request, 'jobInterview_Q14.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_14 = request.POST.get("message")

		if len(response_14) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_14)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_14 = response_14, label14 = label, positive14 = positive, negative14 = negative, 
			neutral14 = neutral, score14 = final_score)
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
		return render(request, 'jobInterview_Q15.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_15 = request.POST.get("message")

		if len(response_15) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_15)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_15 = response_15, label15 = label, positive15 = positive, negative15 = negative, 
			neutral15 = neutral, score15 = final_score)
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
		return render(request, 'jobInterview_Q16.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_16 = request.POST.get("message")

		if len(response_16) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_16)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_16 = response_16, label16 = label, positive16 = positive, negative16 = negative, 
			neutral16 = neutral, score16 = final_score)
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
		return render(request, 'jobInterview_Q17.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_17 = request.POST.get("message")
		
		if len(response_17) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_17)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_17 = response_17, label17 = label, positive17 = positive, negative17 = negative, 
			neutral17 = neutral, score17 = final_score)
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
		return render(request, 'jobInterview_Q18.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_18 = request.POST.get("message")

		if len(response_18) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_18)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_18 = response_18, label18 = label, positive18 = positive, negative18 = negative, 
			neutral18 = neutral, score18 = final_score)
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
		return render(request, 'jobInterview_Q19.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_19 = request.POST.get("message")

		if len(response_19) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_19)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_19 = response_19, label19 = label, positive19 = positive, negative19 = negative, 
			neutral19 = neutral, score19 = final_score)
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
		return render(request, 'jobInterview_Q20.html', context)

	def post(self, request):
		user = request.user
		job_id = request.session['job']
		job_weight = request.POST.get("job-weight")
		response_20 = request.POST.get("message")

		if len(response_20) > 0:
			# use Text-Proccessing API
			json_object = textProccessing(response_20)

			# getting the scores
			dict_response = json_object.get('probability')
			label = json_object.get('label')
			positive = dict_response.get('pos')
			negative = dict_response.get('neg')
			neutral = dict_response.get('neutral')
		else:
			label = None
			positive = 0
			negative = 0
			neutral = 0

		# get final score
		final_score = finalScoring(positive, job_weight)

		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(
			response_20 = response_20, label20 = label, positive20 = positive, negative20 = negative, 
			neutral20 = neutral, score20 = final_score)

		try:
			del request.session['job']
		except KeyError:
			pass
		return redirect('user:interview_success_view')

class InterviewSuccessView(View):
	def get(self, request):
		try:
			if request.user.staff:
				return redirect('administrator:access_denied_view')

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

# def getCleanedText(text):
# 	# converting to lowercase
# 	lower_text = text.lower()

# 	# removing punctuations
# 	cleaned_text = lower_text.translate(str.maketrans('','', string.punctuation))

# 	# splitting text into words
# 	tokenized_words = cleaned_text.split()

# 	stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
#               "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
#               "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these",
#               "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
#               "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
#               "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before",
#               "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
#               "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
#               "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
#               "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
# 	final_words = []

# 	# removing stopwords
# 	for word in tokenized_words:
# 	    if word not in stop_words:
# 	        final_words.append(word)

# 	return " ".join(final_words)

# def sentiment_analyze(sentiment_text):
# 	score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
# 	print(score)