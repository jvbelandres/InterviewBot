from .forms import *
from user.tokens import account_activation_token
from user.models import Account, CreateJob, AppliedJob, Questions

from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, FormView

from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMessage

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site

class DashboardView(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')

		admin_joblist = request.GET.get('job-list-filter')
		if admin_joblist == None:
			admin_joblist = 'All Job Offerings'

		if request.user.admin:
			if admin_joblist == 'All Job Offerings':
				joblists = CreateJob.objects.filter(is_deleted=0)
			else:
				joblists = CreateJob.objects.raw('SELECT "JobOfferings".* FROM "JobOfferings", "Account" WHERE "JobOfferings".is_deleted = False AND "Account".email = \''+ str(admin_joblist) + '\' AND "JobOfferings".admin_id = "Account".id')
		else:
			joblists = CreateJob.objects.filter(admin_id=request.user.id, is_deleted=0)
		appliedJobs = AppliedJob.objects.raw('SELECT * FROM "AppliedJob" WHERE final_score <> 0')

		accounts = Account.objects.filter(staff=1, is_active=1)

		context = {
			'joblists': joblists,
			'appliedJobs': appliedJobs,
			'accounts': accounts,
			'admin_joblist': admin_joblist,
		}
		return render(request, 'admin_dashboard.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnJobId' in request.POST: # when bar chart is clicked by the administrator
				job_id = request.POST.get("job-id")
				request.session['job'] = job_id
				return redirect('administrator:applicants_view')

			jobTitle = request.POST.get("name-title")
			jobDescription = request.POST.get("name-description")
			checkbox = request.POST.get("defaultQ")
			
			q11 = request.POST.get("create-o-qtn11")
			q12 = request.POST.get("create-o-qtn12")
			q13 = request.POST.get("create-o-qtn13")
			q14 = request.POST.get("create-o-qtn14")
			q15 = request.POST.get("create-o-qtn15")
			q16 = request.POST.get("create-o-qtn16")
			q17 = request.POST.get("create-o-qtn17")
			q18 = request.POST.get("create-o-qtn18")
			q19 = request.POST.get("create-o-qtn19")
			q20 = request.POST.get("create-o-qtn20")

			w11 = request.POST.get("create-o-weight11")
			w12 = request.POST.get("create-o-weight12")
			w13 = request.POST.get("create-o-weight13")
			w14 = request.POST.get("create-o-weight14")
			w15 = request.POST.get("create-o-weight15")
			w16 = request.POST.get("create-o-weight16")
			w17 = request.POST.get("create-o-weight17")
			w18 = request.POST.get("create-o-weight18")
			w19 = request.POST.get("create-o-weight19")
			w20 = request.POST.get("create-o-weight20")
			
			t11 = request.POST.get("create-o-timer11")
			t12 = request.POST.get("create-o-timer12")
			t13 = request.POST.get("create-o-timer13")
			t14 = request.POST.get("create-o-timer14")
			t15 = request.POST.get("create-o-timer15")
			t16 = request.POST.get("create-o-timer16")
			t17 = request.POST.get("create-o-timer17")
			t18 = request.POST.get("create-o-timer18")
			t19 = request.POST.get("create-o-timer19")
			t20 = request.POST.get("create-o-timer20")

			if checkbox != 'defaultQ':
				q1 = request.POST.get("create-o-qtn1")
				q2 = request.POST.get("create-o-qtn2")
				q3 = request.POST.get("create-o-qtn3")
				q4 = request.POST.get("create-o-qtn4")
				q5 = request.POST.get("create-o-qtn5")
				q6 = request.POST.get("create-o-qtn6")
				q7 = request.POST.get("create-o-qtn7")
				q8 = request.POST.get("create-o-qtn8")
				q9 = request.POST.get("create-o-qtn9")
				q10 = request.POST.get("create-o-qtn10")
				w1 = request.POST.get("create-o-weight1")
				w2 = request.POST.get("create-o-weight2")
				w3 = request.POST.get("create-o-weight3")
				w4 = request.POST.get("create-o-weight4")
				w5 = request.POST.get("create-o-weight5")
				w6 = request.POST.get("create-o-weight6")
				w7 = request.POST.get("create-o-weight7")
				w8 = request.POST.get("create-o-weight8")
				w9 = request.POST.get("create-o-weight9")
				w10 = request.POST.get("create-o-weight10")
				t1 = request.POST.get("create-o-timer1")
				t2 = request.POST.get("create-o-timer2")
				t3 = request.POST.get("create-o-timer3")
				t4 = request.POST.get("create-o-timer4")
				t5 = request.POST.get("create-o-timer5")
				t6 = request.POST.get("create-o-timer6")
				t7 = request.POST.get("create-o-timer7")
				t8 = request.POST.get("create-o-timer8")
				t9 = request.POST.get("create-o-timer9")
				t10 = request.POST.get("create-o-timer10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=request.user.id)
				form_joboffering.save()
				form_questions = Questions(
					job_id=form_joboffering.id, is_default=0, question_1=q1,question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6, question_7=q7, question_8=q8,
					question_9=q9, question_10=q10, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, 
					question_17=q17, question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, 
					weight7=w7, weight8=w8, weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17,
					weight18=w18, weight19=w19, weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, 
					timer11=t11, timer12=t12, timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20)
			else:
				q1 = request.POST.get("create-d-qtn1")
				q2 = request.POST.get("create-d-qtn2")
				q3 = request.POST.get("create-d-qtn3")
				q4 = request.POST.get("create-d-qtn4")
				q5 = request.POST.get("create-d-qtn5")
				q6 = request.POST.get("create-d-qtn6")
				q7 = request.POST.get("create-d-qtn7")
				q8 = request.POST.get("create-d-qtn8")
				q9 = request.POST.get("create-d-qtn9")
				q10 = request.POST.get("create-d-qtn10")
				t1 = request.POST.get("create-d-timer1")
				t2 = request.POST.get("create-d-timer2")
				t3 = request.POST.get("create-d-timer3")
				t4 = request.POST.get("create-d-timer4")
				t5 = request.POST.get("create-d-timer5")
				t6 = request.POST.get("create-d-timer6")
				t7 = request.POST.get("create-d-timer7")
				t8 = request.POST.get("create-d-timer8")
				t9 = request.POST.get("create-d-timer9")
				t10 = request.POST.get("create-d-timer10")
				w1 = request.POST.get("create-d-weight1")
				w2 = request.POST.get("create-d-weight2")
				w3 = request.POST.get("create-d-weight3")
				w4 = request.POST.get("create-d-weight4")
				w5 = request.POST.get("create-d-weight5")
				w6 = request.POST.get("create-d-weight6")
				w7 = request.POST.get("create-d-weight7")
				w8 = request.POST.get("create-d-weight8")
				w9 = request.POST.get("create-d-weight9")
				w10 = request.POST.get("create-d-weight10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=request.user.id)
				form_joboffering.save()
				form_questions = Questions(
					job_id=form_joboffering.id, is_default=1, question_1=q1,question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6, question_7=q7, question_8=q8,
					question_9=q9, question_10=q10, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, 
					question_17=q17, question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, 
					weight7=w7, weight8=w8, weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17,
					weight18=w18, weight19=w19, weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, 
					timer11=t11, timer12=t12, timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20)
			form_questions.save()
			return redirect('administrator:job-lists_view')

class JobListsView(View):
	def get(self, request):
		user = request.user
		if not user.staff:
			return redirect('user:access_denied_view')

		accounts = Account.objects.filter(staff=1, is_active=1)
		# Raw query to get DISTINCT job_id since required ang primary key if apilon siyas GROUP BY or DISTINCT
		appliedjobs = AppliedJob.objects.raw('SELECT * FROM (SELECT id, job_id, ROW_NUMBER() OVER (PARTITION BY job_id) AS RowNumber FROM "AppliedJob" WHERE final_score IS NOT NULL) AS a WHERE a.RowNumber = 1;')

		admin_joblist = request.GET.get('job-list-filter')
		if admin_joblist == None:
			admin_joblist = 'All Job Offerings'

		if user.admin:
			if admin_joblist == 'All Job Offerings':
				joblists = CreateJob.objects.raw('SELECT "Account".email, "JobOfferings".*, "job_questions".* FROM "Account", "JobOfferings", "job_questions" WHERE "JobOfferings".admin_id = "Account".id AND "JobOfferings".is_deleted = False AND "job_questions".job_id = "JobOfferings".id')
			else:
				joblists = CreateJob.objects.raw('SELECT "Account".email, "JobOfferings".*, "job_questions".* FROM "JobOfferings", "Account", "job_questions" WHERE "JobOfferings".is_deleted = False AND "Account".email = \''+ str(admin_joblist) + '\' AND "JobOfferings".admin_id = "Account".id AND "job_questions".job_id = "JobOfferings".id')
		elif user.staff:
			joblists = CreateJob.objects.raw('SELECT "Account".email, "JobOfferings".*, "job_questions".* FROM "JobOfferings", "Account", "job_questions" WHERE "JobOfferings".is_deleted = False AND "JobOfferings".admin_id = " + str(user.id) + " AND "job_questions".job_id = "JobOfferings".id AND "JobOfferings".admin_id = "Account".id')
			

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
			'accounts': accounts,
			'admin_joblist': admin_joblist,
			'appliedjobs': appliedjobs,
		}

		return render(request, 'admin_joblist.html', context)

	def post(self, request):
		user = request.user
		if 'btnDelete' in request.POST:
			job_id = request.POST.get("id-job")
			CreateJob.objects.filter(id=job_id).update(is_deleted=1)
			messages.error(request, 'deleted')
			return redirect('administrator:job-lists_view')
		elif 'btnUpdate' in request.POST:
			job_id = request.POST.get("job-id")
			title = request.POST.get("job-title")
			description = request.POST.get("job-description")
			is_default = request.POST.get("is_default")
			timer11 = request.POST.get("o-timer11")
			timer12 = request.POST.get("o-timer12")
			timer13 = request.POST.get("o-timer13")
			timer14 = request.POST.get("o-timer14")
			timer15 = request.POST.get("o-timer15")
			timer16 = request.POST.get("o-timer16")
			timer17 = request.POST.get("o-timer17")
			timer18 = request.POST.get("o-timer18")
			timer19 = request.POST.get("o-timer19")
			timer20 = request.POST.get("o-timer20")
			weight11 = request.POST.get("o-weight11")
			weight12 = request.POST.get("o-weight12")
			weight13 = request.POST.get("o-weight13")
			weight14 = request.POST.get("o-weight14")
			weight15 = request.POST.get("o-weight15")
			weight16 = request.POST.get("o-weight16")
			weight17 = request.POST.get("o-weight17")
			weight18 = request.POST.get("o-weight18")
			weight19 = request.POST.get("o-weight19")
			weight20 = request.POST.get("o-weight20")
			q11 = request.POST.get("o-qtn11")
			q12 = request.POST.get("o-qtn12")
			q13 = request.POST.get("o-qtn13")
			q14 = request.POST.get("o-qtn14")
			q15 = request.POST.get("o-qtn15")
			q16 = request.POST.get("o-qtn16")
			q17 = request.POST.get("o-qtn17")
			q18 = request.POST.get("o-qtn18")
			q19 = request.POST.get("o-qtn19")
			q20 = request.POST.get("o-qtn20")

			if is_default == "1":
				print("NOW IN DEFAULT >>>>>>>>>> ")
				weight1 = request.POST.get("d-weight1")
				weight2 = request.POST.get("d-weight2")
				weight3 = request.POST.get("d-weight3")
				weight4 = request.POST.get("d-weight4")
				weight5 = request.POST.get("d-weight5")
				weight6 = request.POST.get("d-weight6")
				weight7 = request.POST.get("d-weight7")
				weight8 = request.POST.get("d-weight8")
				weight9 = request.POST.get("d-weight9")
				weight10 = request.POST.get("d-weight10")
				timer1 = request.POST.get("d-timer1")
				timer2 = request.POST.get("d-timer2")
				timer3 = request.POST.get("d-timer3")
				timer4 = request.POST.get("d-timer4")
				timer5 = request.POST.get("d-timer5")
				timer6 = request.POST.get("d-timer6")
				timer7 = request.POST.get("d-timer7")
				timer8 = request.POST.get("d-timer8")
				timer9 = request.POST.get("d-timer9")
				timer10 = request.POST.get("d-timer10")
				q1 = request.POST.get("d-qtn1")
				q2 = request.POST.get("d-qtn2")
				q3 = request.POST.get("d-qtn3")
				q4 = request.POST.get("d-qtn4")
				q5 = request.POST.get("d-qtn5")
				q6 = request.POST.get("d-qtn6")
				q7 = request.POST.get("d-qtn7")
				q8 = request.POST.get("d-qtn8")
				q9 = request.POST.get("d-qtn9")
				q10 = request.POST.get("d-qtn10")

				CreateJob.objects.filter(id=job_id).update(title=title, description=description)
				Questions.objects.filter(job_id=job_id).update(
				question_1=q1, question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6,
				question_7=q7, question_8=q8, question_9=q9, question_10=q10,question_11=q11, question_12=q12, 
				question_13=q13, question_14=q14, question_15=q15, question_16=q16, question_17=q17, 
				question_18=q18, question_19=q19, question_20=q20, weight1=weight1, weight2=weight2, 
				weight3=weight3, weight4=weight4, weight5=weight5, weight6=weight6, weight7=weight7, 
				weight8=weight8, weight9=weight9, weight10=weight10, weight11=weight11, weight12=weight12,
				weight13=weight13, weight14=weight14, weight15=weight15, weight16=weight16, weight17=weight17,
				weight18=weight18, weight19=weight19, weight20=weight20, timer1=timer1, timer2=timer2, 
				timer3=timer3, timer4=timer4, timer5=timer5, timer6=timer6, timer7=timer7, timer8=timer8,
				timer9=timer9,timer10=timer10, timer11=timer11, timer12=timer12, timer13=timer13, timer14=timer14,
				timer15=timer15, timer16=timer16, timer17=timer17, timer18=timer18, timer19=timer19, timer20=timer20)
			else:
				weight1 = request.POST.get("o-weight1")
				weight2 = request.POST.get("o-weight2")
				weight3 = request.POST.get("o-weight3")
				weight4 = request.POST.get("o-weight4")
				weight5 = request.POST.get("o-weight5")
				weight6 = request.POST.get("o-weight6")
				weight7 = request.POST.get("o-weight7")
				weight8 = request.POST.get("o-weight8")
				weight9 = request.POST.get("o-weight9")
				weight10 = request.POST.get("o-weight10")
				timer1 = request.POST.get("o-timer1")
				timer2 = request.POST.get("o-timer2")
				timer3 = request.POST.get("o-timer3")
				timer4 = request.POST.get("o-timer4")
				timer5 = request.POST.get("o-timer5")
				timer6 = request.POST.get("o-timer6")
				timer7 = request.POST.get("o-timer7")
				timer8 = request.POST.get("o-timer8")
				timer9 = request.POST.get("o-timer9")
				timer10 = request.POST.get("o-timer10")
				q1 = request.POST.get("o-qtn1")
				q2 = request.POST.get("o-qtn2")
				q3 = request.POST.get("o-qtn3")
				q4 = request.POST.get("o-qtn4")
				q5 = request.POST.get("o-qtn5")
				q6 = request.POST.get("o-qtn6")
				q7 = request.POST.get("o-qtn7")
				q8 = request.POST.get("o-qtn8")
				q9 = request.POST.get("o-qtn9")
				q10 = request.POST.get("o-qtn10")

				CreateJob.objects.filter(id=job_id).update(title=title, description=description)
				Questions.objects.filter(job_id=job_id).update(
					question_1=q1, question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6,
					question_7=q7, question_8=q8, question_9=q9, question_10=q10,question_11=q11, question_12=q12, 
					question_13=q13, question_14=q14, question_15=q15, question_16=q16, question_17=q17, 
					question_18=q18, question_19=q19, question_20=q20, weight1=weight1, weight2=weight2, 
					weight3=weight3, weight4=weight4, weight5=weight5, weight6=weight6, weight7=weight7, 
					weight8=weight8, weight9=weight9, weight10=weight10, weight11=weight11, weight12=weight12,
					weight13=weight13, weight14=weight14, weight15=weight15, weight16=weight16, weight17=weight17,
					weight18=weight18, weight19=weight19, weight20=weight20, timer1=timer1, timer2=timer2, 
					timer3=timer3, timer4=timer4, timer5=timer5, timer6=timer6, timer7=timer7, timer8=timer8,
					timer9=timer9,timer10=timer10, timer11=timer11, timer12=timer12, timer13=timer13, timer14=timer14,
					timer15=timer15, timer16=timer16, timer17=timer17, timer18=timer18, timer19=timer19, timer20=timer20)

			messages.success(request, 'updated')
			return redirect('administrator:job-lists_view')
		elif 'btnAdd' in request.POST:
			jobTitle = request.POST.get("name-title")
			jobDescription = request.POST.get("name-description")
			checkbox = request.POST.get("defaultQ")
			
			q11 = request.POST.get("create-o-qtn11")
			q12 = request.POST.get("create-o-qtn12")
			q13 = request.POST.get("create-o-qtn13")
			q14 = request.POST.get("create-o-qtn14")
			q15 = request.POST.get("create-o-qtn15")
			q16 = request.POST.get("create-o-qtn16")
			q17 = request.POST.get("create-o-qtn17")
			q18 = request.POST.get("create-o-qtn18")
			q19 = request.POST.get("create-o-qtn19")
			q20 = request.POST.get("create-o-qtn20")

			w11 = request.POST.get("create-o-weight11")
			w12 = request.POST.get("create-o-weight12")
			w13 = request.POST.get("create-o-weight13")
			w14 = request.POST.get("create-o-weight14")
			w15 = request.POST.get("create-o-weight15")
			w16 = request.POST.get("create-o-weight16")
			w17 = request.POST.get("create-o-weight17")
			w18 = request.POST.get("create-o-weight18")
			w19 = request.POST.get("create-o-weight19")
			w20 = request.POST.get("create-o-weight20")
			
			t11 = request.POST.get("create-o-timer11")
			t12 = request.POST.get("create-o-timer12")
			t13 = request.POST.get("create-o-timer13")
			t14 = request.POST.get("create-o-timer14")
			t15 = request.POST.get("create-o-timer15")
			t16 = request.POST.get("create-o-timer16")
			t17 = request.POST.get("create-o-timer17")
			t18 = request.POST.get("create-o-timer18")
			t19 = request.POST.get("create-o-timer19")
			t20 = request.POST.get("create-o-timer20")

			if checkbox != 'defaultQ':
				q1 = request.POST.get("create-o-qtn1")
				q2 = request.POST.get("create-o-qtn2")
				q3 = request.POST.get("create-o-qtn3")
				q4 = request.POST.get("create-o-qtn4")
				q5 = request.POST.get("create-o-qtn5")
				q6 = request.POST.get("create-o-qtn6")
				q7 = request.POST.get("create-o-qtn7")
				q8 = request.POST.get("create-o-qtn8")
				q9 = request.POST.get("create-o-qtn9")
				q10 = request.POST.get("create-o-qtn10")
				w1 = request.POST.get("create-o-weight1")
				w2 = request.POST.get("create-o-weight2")
				w3 = request.POST.get("create-o-weight3")
				w4 = request.POST.get("create-o-weight4")
				w5 = request.POST.get("create-o-weight5")
				w6 = request.POST.get("create-o-weight6")
				w7 = request.POST.get("create-o-weight7")
				w8 = request.POST.get("create-o-weight8")
				w9 = request.POST.get("create-o-weight9")
				w10 = request.POST.get("create-o-weight10")
				t1 = request.POST.get("create-o-timer1")
				t2 = request.POST.get("create-o-timer2")
				t3 = request.POST.get("create-o-timer3")
				t4 = request.POST.get("create-o-timer4")
				t5 = request.POST.get("create-o-timer5")
				t6 = request.POST.get("create-o-timer6")
				t7 = request.POST.get("create-o-timer7")
				t8 = request.POST.get("create-o-timer8")
				t9 = request.POST.get("create-o-timer9")
				t10 = request.POST.get("create-o-timer10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=user.id)
				form_joboffering.save()
				form_questions = Questions(job_id=form_joboffering.id, is_default=0, question_1=q1,question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6, question_7=q7, question_8=q8,
				question_9=q9, question_10=q10, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, 
				question_17=q17, question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, 
				weight7=w7, weight8=w8, weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17,
	            weight18=w18, weight19=w19, weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, 
				timer11=t11, timer12=t12, timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20)
			else:
				t1 = request.POST.get("create-d-timer1")
				t2 = request.POST.get("create-d-timer2")
				t3 = request.POST.get("create-d-timer3")
				t4 = request.POST.get("create-d-timer4")
				t5 = request.POST.get("create-d-timer5")
				t6 = request.POST.get("create-d-timer6")
				t7 = request.POST.get("create-d-timer7")
				t8 = request.POST.get("create-d-timer8")
				t9 = request.POST.get("create-d-timer9")
				t10 = request.POST.get("create-d-timer10")
				w1 = request.POST.get("create-d-weight1")
				w2 = request.POST.get("create-d-weight2")
				w3 = request.POST.get("create-d-weight3")
				w4 = request.POST.get("create-d-weight4")
				w5 = request.POST.get("create-d-weight5")
				w6 = request.POST.get("create-d-weight6")
				w7 = request.POST.get("create-d-weight7")
				w8 = request.POST.get("create-d-weight8")
				w9 = request.POST.get("create-d-weight9")
				w10 = request.POST.get("create-d-weight10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=user.id)
				form_joboffering.save()
				form_questions = Questions(job_id=form_joboffering.id, is_default=1, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, question_17=q17, 
					question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, weight7=w7, weight8=w8, 
					weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17, weight18=w18, weight19=w19, 
					weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, timer11=t11, timer12=t12, 
					timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20,)
			form_questions.save()
			return redirect('administrator:job-lists_view')

		elif 'viewApplicant' in request.POST:
			jobID1 = request.POST.get("jobID1")
			request.session['job'] = jobID1
			return redirect('administrator:applicants_view')

class AdminRegistrationView(CreateView):
	form_class = AdminRegisterForm
	template_name = 'register_admin.html'

	def form_valid(self, form):
		user = form.save(commit=False)
		user.is_active = False
		user.admin = True
		user.staff = True
		user.is_active = False
		pw = form.cleaned_data.get('password')
		user.set_password(pw)
		user.save() # If dili mag user.save() kay dili mu gana ang token
		current_site = get_current_site(self.request)
		mail_subject = 'Activate your administrator account.'
		message = render_to_string('account_activation/administrator/spAcc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
            'type': 'administrator',
	    })
		to_email = form.cleaned_data.get('email')
		email = EmailMessage(
					mail_subject, message, to=[to_email]
		)
		email.send()
		self.request.session['email'] = to_email
		return redirect('administrator:registration_complete')

	def form_invalid(self, form):
		messages.error(self.request, 'Invalid email. Please try another.')
		return super().form_invalid(form)

class StaffRegistrationView(CreateView):
	form_class = StaffRegisterForm
	template_name = 'register_staff.html'
	
	def form_valid(self, form):
		user = form.save(commit=False)
		user.is_active = False
		user.staff = True
		pw = form.cleaned_data.get('password')
		user.set_password(pw)
		user.save()
		current_site = get_current_site(self.request)
		mail_subject = 'Activate your staff account.'
		message = render_to_string('account_activation/administrator/spAcc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
            'type': 'staff',
	    })
		to_email = form.cleaned_data.get('email')
		email = EmailMessage(
					mail_subject, message, to=[to_email]
		)
		email.send()
		self.request.session['email'] = to_email
		return redirect('administrator:registration_complete')

	def form_invalid(self, form):
		messages.error(self.request, 'Invalid email. Please try another.')
		return super().form_invalid(form)

# Method for account activation
def sp_activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64).decode())
		user = Account.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		return redirect('administrator:activate-success')
	else:
		return redirect('administrator:activate-failed')

class RegisterComplete(View): # After staff and administrator registration
	def get(self, request):
		try:
			email = request.session['email']
			return render(request, 'account_activation/administrator/account_register_done.html', {'email': email})
		except:
			return redirect('administrator:dashboard_view')

class SpActivationSuccess(View): # If account activation succeed
	def get(self, request):
		return render(request, 'account_activation/administrator/spAcc_activation_success.html')

class SpActivationFailed(View): # If account activation failed
	def get(self, request):
		return render(request, 'account_activation/administrator/spAcc_activation_failed.html')

class SettingsView(FormView):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		return render(request, 'admin_settings.html')

	def post(self, request):
		user = request.user
		if 'btnUpdate' in request.POST:
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
			messages.success(request, 'Account Information Updated')
			return redirect('administrator:settings_view')
		elif 'btnAdd' in request.POST:
			jobTitle = request.POST.get("name-title")
			jobDescription = request.POST.get("name-description")
			checkbox = request.POST.get("defaultQ")
			
			q11 = request.POST.get("create-o-qtn11")
			q12 = request.POST.get("create-o-qtn12")
			q13 = request.POST.get("create-o-qtn13")
			q14 = request.POST.get("create-o-qtn14")
			q15 = request.POST.get("create-o-qtn15")
			q16 = request.POST.get("create-o-qtn16")
			q17 = request.POST.get("create-o-qtn17")
			q18 = request.POST.get("create-o-qtn18")
			q19 = request.POST.get("create-o-qtn19")
			q20 = request.POST.get("create-o-qtn20")

			w11 = request.POST.get("create-o-weight11")
			w12 = request.POST.get("create-o-weight12")
			w13 = request.POST.get("create-o-weight13")
			w14 = request.POST.get("create-o-weight14")
			w15 = request.POST.get("create-o-weight15")
			w16 = request.POST.get("create-o-weight16")
			w17 = request.POST.get("create-o-weight17")
			w18 = request.POST.get("create-o-weight18")
			w19 = request.POST.get("create-o-weight19")
			w20 = request.POST.get("create-o-weight20")
			
			t11 = request.POST.get("create-o-timer11")
			t12 = request.POST.get("create-o-timer12")
			t13 = request.POST.get("create-o-timer13")
			t14 = request.POST.get("create-o-timer14")
			t15 = request.POST.get("create-o-timer15")
			t16 = request.POST.get("create-o-timer16")
			t17 = request.POST.get("create-o-timer17")
			t18 = request.POST.get("create-o-timer18")
			t19 = request.POST.get("create-o-timer19")
			t20 = request.POST.get("create-o-timer20")

			if checkbox != 'defaultQ':
				q1 = request.POST.get("create-o-qtn1")
				q2 = request.POST.get("create-o-qtn2")
				q3 = request.POST.get("create-o-qtn3")
				q4 = request.POST.get("create-o-qtn4")
				q5 = request.POST.get("create-o-qtn5")
				q6 = request.POST.get("create-o-qtn6")
				q7 = request.POST.get("create-o-qtn7")
				q8 = request.POST.get("create-o-qtn8")
				q9 = request.POST.get("create-o-qtn9")
				q10 = request.POST.get("create-o-qtn10")
				w1 = request.POST.get("create-o-weight1")
				w2 = request.POST.get("create-o-weight2")
				w3 = request.POST.get("create-o-weight3")
				w4 = request.POST.get("create-o-weight4")
				w5 = request.POST.get("create-o-weight5")
				w6 = request.POST.get("create-o-weight6")
				w7 = request.POST.get("create-o-weight7")
				w8 = request.POST.get("create-o-weight8")
				w9 = request.POST.get("create-o-weight9")
				w10 = request.POST.get("create-o-weight10")
				t1 = request.POST.get("create-o-timer1")
				t2 = request.POST.get("create-o-timer2")
				t3 = request.POST.get("create-o-timer3")
				t4 = request.POST.get("create-o-timer4")
				t5 = request.POST.get("create-o-timer5")
				t6 = request.POST.get("create-o-timer6")
				t7 = request.POST.get("create-o-timer7")
				t8 = request.POST.get("create-o-timer8")
				t9 = request.POST.get("create-o-timer9")
				t10 = request.POST.get("create-o-timer10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=user.id)
				form_joboffering.save()
				form_questions = Questions(
					job_id=form_joboffering.id, is_default=0, question_1=q1,question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6, question_7=q7, question_8=q8,
					question_9=q9, question_10=q10, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, 
					question_17=q17, question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, 
					weight7=w7, weight8=w8, weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17,
					weight18=w18, weight19=w19, weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, 
					timer11=t11, timer12=t12, timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20)
			else:
				q1 = request.POST.get("create-d-qtn1")
				q2 = request.POST.get("create-d-qtn2")
				q3 = request.POST.get("create-d-qtn3")
				q4 = request.POST.get("create-d-qtn4")
				q5 = request.POST.get("create-d-qtn5")
				q6 = request.POST.get("create-d-qtn6")
				q7 = request.POST.get("create-d-qtn7")
				q8 = request.POST.get("create-d-qtn8")
				q9 = request.POST.get("create-d-qtn9")
				q10 = request.POST.get("create-d-qtn10")
				t1 = request.POST.get("create-d-timer1")
				t2 = request.POST.get("create-d-timer2")
				t3 = request.POST.get("create-d-timer3")
				t4 = request.POST.get("create-d-timer4")
				t5 = request.POST.get("create-d-timer5")
				t6 = request.POST.get("create-d-timer6")
				t7 = request.POST.get("create-d-timer7")
				t8 = request.POST.get("create-d-timer8")
				t9 = request.POST.get("create-d-timer9")
				t10 = request.POST.get("create-d-timer10")
				w1 = request.POST.get("create-d-weight1")
				w2 = request.POST.get("create-d-weight2")
				w3 = request.POST.get("create-d-weight3")
				w4 = request.POST.get("create-d-weight4")
				w5 = request.POST.get("create-d-weight5")
				w6 = request.POST.get("create-d-weight6")
				w7 = request.POST.get("create-d-weight7")
				w8 = request.POST.get("create-d-weight8")
				w9 = request.POST.get("create-d-weight9")
				w10 = request.POST.get("create-d-weight10")

				form_joboffering = CreateJob(title=jobTitle, description=jobDescription, admin_id=user.id)
				form_joboffering.save()
				form_questions = Questions(
					job_id=form_joboffering.id, is_default=0, question_1=q1,question_2=q2, question_3=q3, question_4=q4, question_5=q5, question_6=q6, question_7=q7, question_8=q8,
					question_9=q9, question_10=q10, question_11=q11, question_12=q12, question_13=q13, question_14=q14, question_15=q15, question_16=q16, 
					question_17=q17, question_18=q18, question_19=q19, question_20=q20, weight1=w1, weight2=w2, weight3=w3, weight4=w4, weight5=w5, weight6=w6, 
					weight7=w7, weight8=w8, weight9=w9, weight10=w10, weight11=w11, weight12=w12, weight13=w13, weight14=w14, weight15=w15, weight16=w16, weight17=w17,
					weight18=w18, weight19=w19, weight20=w20, timer1=t1, timer2=t2, timer3=t3, timer4=t4, timer5=t5, timer6=t6, timer7=t7, timer8=t8, timer9=t9, timer10=t10, 
					timer11=t11, timer12=t12, timer13=t13, timer14=t14, timer15=t15, timer16=t16, timer17=t17, timer18=t18, timer19=t19, timer20=t20)
			form_questions.save()
			return redirect('administrator:job-lists_view')

class Applicants(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		job_id = request.session['job']
		joblists = CreateJob.objects.filter(id = job_id)
		applicants = Account.objects.raw('SELECT DISTINCT "Account".id,firstname,lastname,"AppliedJob".final_score FROM "Account","JobOfferings","AppliedJob" WHERE "AppliedJob".job_id =' + str(job_id) +' AND "Account".id = "AppliedJob".user_id ORDER BY "AppliedJob".final_score DESC')
		
		context = {
			'joblists': joblists,
			'applicants': applicants
		}
		return render(request, 'job_applicants.html', context)

	def post(self, request):
		if request.method == 'POST':
			if 'btnAnswers' in request.POST:
				request.session['applicant'] = request.POST.get("applicantID")
				job_id = request.session['job']
				return redirect('administrator:response_view')
		else:
			return render(request, 'job_applicants.html')

class ResponseView(View):
	def get(self, request):
		if not request.user.staff:
			return redirect('user:access_denied_view')
		job_id = request.session['job']
		applicant_id = request.session['applicant']
		# SELECT * FROM (SELECT id, job_id, ROW_NUMBER() OVER (PARTITION BY job_id) AS RowNumber FROM "AppliedJob" WHERE final_score IS NOT NULL) AS a WHERE a.RowNumber = 1;
		response = AppliedJob.objects.raw('SELECT * FROM "AppliedJob","JobOfferings","Account" WHERE "AppliedJob".job_id = "JobOfferings".id AND "AppliedJob".user_id = "Account".id AND "JobOfferings".id = '+str(job_id)+' AND "Account".id = '+str(applicant_id)+' GROUP BY "Account".id')
		job = CreateJob.objects.filter(id = job_id)

		context = {
			'responses': response,
			'job': job,
		}
		return render(request, 'individual_applicant.html', context)

class LogOutView(View):
	def get(self, request):
		logout(request)
		return render(request, 'log_out.html')

class AdminAccessDeniedView(View):
	def get(self, request):
		return render(request, 'admin_access_denied.html')