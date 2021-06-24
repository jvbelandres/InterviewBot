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

		if request.user.admin:
			joblists = CreateJob.objects.filter(is_deleted=0)
		else:
			joblists = CreateJob.objects.filter(admin_id=request.user.id, is_deleted=0)
		appliedJobs = AppliedJob.objects.all()

		context = {
			'joblists': joblists,
			'appliedJobs': appliedJobs
		}
		return render(request, 'admindashboard.html', context)

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
		w1 = request.POST.get("weight1")
		w2 = request.POST.get("weight2")
		w3 = request.POST.get("weight3")
		w4 = request.POST.get("weight4")
		w5 = request.POST.get("weight5")
		w6 = request.POST.get("weight6")
		w7 = request.POST.get("weight7")
		w8 = request.POST.get("weight8")
		w9 = request.POST.get("weight9")
		w10 = request.POST.get("weight10")
		t1 = request.POST.get("timer1")
		t2 = request.POST.get("timer2")
		t3 = request.POST.get("timer3")
		t4 = request.POST.get("timer4")
		t5 = request.POST.get("timer5")
		t6 = request.POST.get("timer6")
		t7 = request.POST.get("timer7")
		t8 = request.POST.get("timer8")
		t9 = request.POST.get("timer9")
		t10 = request.POST.get("timer10")

		form = CreateJob(title = jobTitle, description = jobDescription,
            question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
            question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
            question_19 = q19, question_20 = q20, weight1 = w1, weight2 = w2, weight3 = w3,
            weight4 = w4, weight5 = w5, weight6 = w6, weight7 = w7, weight8 = w8, weight9 = w9,
            weight10 = w10, timer1 = t1, timer2 = t2, timer3 = t3, timer4 = t4, timer5 = t5,
            timer6 = t6, timer7 = t7, timer8 = t8, timer9 = t9, timer10 = t10, admin_id = user.id)
		form.save()
		return redirect('administrator:job-lists_view')

class JobListsView(View):
	def get(self, request):
		user = request.user
		if not user.staff:
			return redirect('user:access_denied_view')

		if user.admin:
			joblists = CreateJob.objects.raw('SELECT account.email, jobofferings.* FROM account, jobofferings WHERE jobofferings.admin_id = account.id AND jobofferings.is_deleted = 0')
		elif user.staff:
			joblists = CreateJob.objects.filter(admin_id = user.id, is_deleted=0)

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
			job = CreateJob.objects.filter(id=jobID1).update(is_deleted=1)
			return redirect('administrator:job-lists_view')
		elif 'btnUpdate' in request.POST:
			job_id = request.POST.get("job-id")
			title = request.POST.get("job-title")
			description = request.POST.get("job-description")
			weight1 = request.POST.get("weight1")
			weight2 = request.POST.get("weight2")
			weight3 = request.POST.get("weight3")
			weight4 = request.POST.get("weight4")
			weight5 = request.POST.get("weight5")
			weight6 = request.POST.get("weight6")
			weight7 = request.POST.get("weight7")
			weight8 = request.POST.get("weight8")
			weight9 = request.POST.get("weight9")
			weight10 = request.POST.get("weight10")
			timer1 = request.POST.get("timer1")
			timer2 = request.POST.get("timer2")
			timer3 = request.POST.get("timer3")
			timer4 = request.POST.get("timer4")
			timer5 = request.POST.get("timer5")
			timer6 = request.POST.get("timer6")
			timer7 = request.POST.get("timer7")
			timer8 = request.POST.get("timer8")
			timer9 = request.POST.get("timer9")
			timer10 = request.POST.get("timer10")
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

			job = CreateJob.objects.filter(id=job_id).update(title=title, description=description,
				question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, 
				question_16=q16, question_17=q17, question_18=q18, question_19=q19, question_20=q20,
				weight1=weight1, weight2=weight2, weight3=weight3, weight4=weight4, weight5=weight5,
				weight6=weight6, weight7=weight7, weight8=weight8, weight9=weight9, weight10=weight10,
				timer1=timer1, timer2=timer2, timer3=timer3, timer4=timer4, timer5=timer5, timer6=timer6,
				timer7=timer7, timer8=timer8,timer9=timer9,timer10=timer10)
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
			w1 = request.POST.get("weight1")
			w2 = request.POST.get("weight2")
			w3 = request.POST.get("weight3")
			w4 = request.POST.get("weight4")
			w5 = request.POST.get("weight5")
			w6 = request.POST.get("weight6")
			w7 = request.POST.get("weight7")
			w8 = request.POST.get("weight8")
			w9 = request.POST.get("weight9")
			w10 = request.POST.get("weight10")
			t1 = request.POST.get("timer1")
			t2 = request.POST.get("timer2")
			t3 = request.POST.get("timer3")
			t4 = request.POST.get("timer4")
			t5 = request.POST.get("timer5")
			t6 = request.POST.get("timer6")
			t7 = request.POST.get("timer7")
			t8 = request.POST.get("timer8")
			t9 = request.POST.get("timer9")
			t10 = request.POST.get("timer10")

			form = CreateJob(title = jobTitle, description = jobDescription,
            question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
            question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
            question_19 = q19, question_20 = q20, weight1 = w1, weight2 = w2, weight3 = w3,
            weight4 = w4, weight5 = w5, weight6 = w6, weight7 = w7, weight8 = w8, weight9 = w9,
            weight10 = w10, timer1 = t1, timer2 = t2, timer3 = t3, timer4 = t4, timer5 = t5,
            timer6 = t6, timer7 = t7, timer8 = t8, timer9 = t9, timer10 = t10, admin_id = user.id)

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
			w1 = request.POST.get("weight1")
			w2 = request.POST.get("weight2")
			w3 = request.POST.get("weight3")
			w4 = request.POST.get("weight4")
			w5 = request.POST.get("weight5")
			w6 = request.POST.get("weight6")
			w7 = request.POST.get("weight7")
			w8 = request.POST.get("weight8")
			w9 = request.POST.get("weight9")
			w10 = request.POST.get("weight10")
			t1 = request.POST.get("timer1")
			t2 = request.POST.get("timer2")
			t3 = request.POST.get("timer3")
			t4 = request.POST.get("timer4")
			t5 = request.POST.get("timer5")
			t6 = request.POST.get("timer6")
			t7 = request.POST.get("timer7")
			t8 = request.POST.get("timer8")
			t9 = request.POST.get("timer9")
			t10 = request.POST.get("timer10")

			form = CreateJob(title = jobTitle, description = jobDescription,
            question_11 = q11, question_12 = q12, question_13 = q13, question_14 = q14,
            question_15 = q15, question_16 = q16, question_17 = q17, question_18 = q18,
            question_19 = q19, question_20 = q20, weight1 = w1, weight2 = w2, weight3 = w3,
            weight4 = w4, weight5 = w5, weight6 = w6, weight7 = w7, weight8 = w8, weight9 = w9,
            weight10 = w10, timer1 = t1, timer2 = t2, timer3 = t3, timer4 = t4, timer5 = t5,
            timer6 = t6, timer7 = t7, timer8 = t8, timer9 = t9, timer10 = t10, admin_id = user.id)
			form.save()
			return redirect('administrator:job-lists_view')

class Applicants(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		job_id = request.session['job']
		joblists = CreateJob.objects.filter(id = job_id)
		applicants = Account.objects.raw('SELECT DISTINCT account.id,firstname,lastname FROM account,jobofferings,appliedjob WHERE appliedjob.job_id =' + str(job_id) +' AND account.id = appliedjob.user_id ORDER BY appliedjob.final_score DESC')
		
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
		response = AppliedJob.objects.raw('SELECT * FROM appliedjob,jobofferings,account WHERE appliedjob.job_id = jobofferings.id AND appliedjob.user_id = account.id AND jobofferings.id = '+str(job_id)+' AND account.id = '+str(applicant_id)+' GROUP BY account.email')
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