from .forms import *
from user.models import Account, CreateJob, AppliedJob

from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, FormView

from django.core.paginator import Paginator
from django.core.mail import send_mail

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

class DashboardView(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		return render(request, 'admindashboard.html')

	def post(self, request):
		user = request.user
		jobTitle = request.POST.get("name-title")
		jobDescription = request.POST.get("name-description")
		q11 = request.POST.get("qtn11")
		q12 = request.POST.get("qtn12")
		q13 = request.POST.get("qtn13")
		q14 = request.POST.get("qtn14")
		q15 = request.POST.get("qtn15")
		q16 = request.POST.get("qtn16")
		q17 = request.POST.get("qtn17")
		q18 = request.POST.get("qtn18")
		q19 = request.POST.get("qtn19")
		q20 = request.POST.get("qtn20")

		form = CreateJob(title = jobTitle, description = jobDescription,
            question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
            question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
            question_19 = q19, question_20 = q20, admin_id = user.id)
		form.save()
		return redirect('administrator:job-lists_view')

class JobListsView(View):
	def get(self, request):
		user = request.user
		if not user.staff:
			return redirect('user:access_denied_view')

		if user.admin:
			joblists = CreateJob.objects.all()
		elif user.staff:
			joblists = CreateJob.objects.filter(admin_id = user.id)

		p = Paginator(joblists,2)
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
		}

		return render(request, 'adminjoblist.html', context)

	def post(self, request):
		user = request.user
		if 'btnDelete' in request.POST:
			jobID1 = request.POST.get("jobID")
			job = CreateJob.objects.filter(id=jobID1).delete()
			return redirect('administrator:job-lists_view')
		elif 'btnUpdate' in request.POST:
			jobID1 = request.POST.get("jobID")
			jobDesription1 = request.POST.get("jobDescription")
			jobHeader1 = request.POST.get("jobHeader")
			job = CreateJob.objects.filter(id=jobID1).update(description = jobDesription1, title= jobHeader1)
			return redirect('administrator:job-lists_view')
		elif 'btnAdd' in request.POST:
			jobTitle = request.POST.get("name-title")
			jobDescription = request.POST.get("name-description")
			q11 = request.POST.get("qtn11")
			q12 = request.POST.get("qtn12")
			q13 = request.POST.get("qtn13")
			q14 = request.POST.get("qtn14")
			q15 = request.POST.get("qtn15")
			q16 = request.POST.get("qtn16")
			q17 = request.POST.get("qtn17")
			q18 = request.POST.get("qtn18")
			q19 = request.POST.get("qtn19")
			q20 = request.POST.get("qtn20")

			form = CreateJob(title = jobTitle, description = jobDescription,
			    question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
			    question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
			    question_19 = q19, question_20 = q20, admin_id = user.id)
			form.save()
			return redirect('administrator:job-lists_view')
		elif 'viewApplicant' in request.POST:
			jobID1 = request.POST.get("jobID1")
			request.session['job'] = jobID1
			return redirect('administrator:applicants_view')

class AdminRegistrationView(CreateView):
	form_class = RegisterForm
	template_name = 'registeradmin.html'
	success_url = '/administrator/dashboard/'

class SettingsView(FormView):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		return render(request, 'adminsettings.html')

	def post(self, request):
		user = request.user
		if 'btnUpdate' in request.POST:
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
			return redirect('administrator:settings_view')
		elif 'btnAdd' in request.POST:
			jobTitle = request.POST.get("name-title")
			jobDescription = request.POST.get("name-description")
			q11 = request.POST.get("qtn11")
			q12 = request.POST.get("qtn12")
			q13 = request.POST.get("qtn13")
			q14 = request.POST.get("qtn14")
			q15 = request.POST.get("qtn15")
			q16 = request.POST.get("qtn16")
			q17 = request.POST.get("qtn17")
			q18 = request.POST.get("qtn18")
			q19 = request.POST.get("qtn19")
			q20 = request.POST.get("qtn20")

			form = CreateJob(title = jobTitle, description = jobDescription,
	            question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
	            question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
	            question_19 = q19, question_20 = q20, admin_id = user.id)
			form.save()
			return redirect('administrator:job-lists_view')

class Applicants(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		job_id = request.session['job']
		joblists = CreateJob.objects.filter(id = job_id)
		applicants = Account.objects.raw('SELECT DISTINCT account.id,firstname,lastname FROM account,jobofferings,appliedjob WHERE appliedjob.job_id =' + str(job_id) +' AND account.id = appliedjob.user_id')
		
		context = {
			'joblists': joblists,
			'applicants': applicants
		}
		return render(request, 'jobApplicants.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnAnswers' in request.POST:
				request.session['applicant'] = request.POST.get("applicantID")
				job_id = request.session['job']
				return redirect('administrator:response_view')
		else:
			return render(request, 'jobApplicants.html')

class ResponseView(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		job_id = request.session['job']
		applicant_id = request.session['applicant']
		response = AppliedJob.objects.raw('SELECT * FROM appliedjob,jobofferings,account where appliedjob.job_id = jobofferings.id and appliedjob.user_id = account.id and jobofferings.id = '+str(job_id)+' and account.id = '+str(applicant_id)+' GROUP BY account.firstname')
		job = CreateJob.objects.filter(id = job_id)

		context = {
			'responses': response,
			'job': job,
		}
		return render(request, 'individualApplicant.html', context)

class LogOutView(View):
	def get(self, request):
		logout(request)
		return render(request, 'LogOut.html')

class AdminAccessDeniedView(View):
	def get(self, request):
		return render(request, 'admin_accessDenied.html')