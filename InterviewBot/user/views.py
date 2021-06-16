from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.utils.datastructures import MultiValueDictKeyError

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .forms import *
from user.models import AppliedJob, SavedJob

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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_1 = response_1)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_2 = response_2)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_3 = response_3)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_4 = response_4)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_5 = response_5)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_6 = response_6)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_7 = response_7)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_8 = response_8)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_9 = response_9)
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
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_10 = response_10)
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
		response_11 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_11 = response_11)
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
		response_12 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_12 = response_12)
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
		response_13 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_13 = response_13)
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
		response_14 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_14 = response_14)
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
		response_15 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_15 = response_15)
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
		response_16 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_16 = response_16)
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
		response_17 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_17 = response_17)
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
		response_18 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_18 = response_18)
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
		response_19 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_19 = response_19)
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
		response_20 = request.POST.get("message")
		update_applyJob = AppliedJob.objects.filter(job_id = job_id, user_id = user.id).update(response_20 = response_20)

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