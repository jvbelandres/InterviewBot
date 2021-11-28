from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

from django.urls import path
from . import views

#path arranged alphabetically by name
app_name= 'user'
urlpatterns=[
    #path('api/data', views.get_data, name='api-data'),

    #TEST URL
    path('about-us/', login_required(views.AboutUsView.as_view()), name="about-us_view"),
    path('contact-us/', login_required(views.ContactUsView.as_view()), name="contact-us_view"),
    path('home', login_required(views.HomePageView.as_view()), name="home_view"),
    path('registration/', views.RegisterView.as_view(), name="registration_view"),
    path('registration/complete/', views.RegisterComplete.as_view(), name="registration_complete"),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('activate/success/', views.ActivationSuccess.as_view(), name="activate-success"),
    path('activate/failed/', views.ActivationFailed.as_view(), name="activate-failed"),
    path('job-offers/', login_required(views.JobOffersView.as_view()), name="job-offers_view"),
    path('settings/', login_required(views.SettingsView.as_view()), name="settings_view"),
    path('logout/', login_required(views.LogOutView.as_view()), name="logout_view"),
    path('denied/', login_required(views.AccessDeniedView.as_view()), name="access_denied_view"),
    path('job-interview/', login_required(views.JobInterviewView.as_view()), name="job-interview_view"),
    path('job-interview/question-1', login_required(views.JobInterviewQ1View.as_view()), name="job-interview_q1"),
    path('job-interview/question-2', login_required(views.JobInterviewQ2View.as_view()), name="job-interview_q2"),
    path('job-interview/question-3', login_required(views.JobInterviewQ3View.as_view()), name="job-interview_q3"),
    path('job-interview/question-4', login_required(views.JobInterviewQ4View.as_view()), name="job-interview_q4"),
    path('job-interview/question-5', login_required(views.JobInterviewQ5View.as_view()), name="job-interview_q5"),
    path('job-interview/question-6', login_required(views.JobInterviewQ6View.as_view()), name="job-interview_q6"),
    path('job-interview/question-7', login_required(views.JobInterviewQ7View.as_view()), name="job-interview_q7"),
    path('job-interview/question-8', login_required(views.JobInterviewQ8View.as_view()), name="job-interview_q8"),
    path('job-interview/question-9', login_required(views.JobInterviewQ9View.as_view()), name="job-interview_q9"),
    path('job-interview/question-10', login_required(views.JobInterviewQ10View.as_view()), name="job-interview_q10"),
    path('job-interview/question-11', login_required(views.JobInterviewQ11View.as_view()), name="job-interview_q11"),
    path('job-interview/question-12', login_required(views.JobInterviewQ12View.as_view()), name="job-interview_q12"),
    path('job-interview/question-13', login_required(views.JobInterviewQ13View.as_view()), name="job-interview_q13"),
    path('job-interview/question-14', login_required(views.JobInterviewQ14View.as_view()), name="job-interview_q14"),
    path('job-interview/question-15', login_required(views.JobInterviewQ15View.as_view()), name="job-interview_q15"),
    path('job-interview/question-16', login_required(views.JobInterviewQ16View.as_view()), name="job-interview_q16"),
    path('job-interview/question-17', login_required(views.JobInterviewQ17View.as_view()), name="job-interview_q17"),
    path('job-interview/question-18', login_required(views.JobInterviewQ18View.as_view()), name="job-interview_q18"),
    path('job-interview/question-19', login_required(views.JobInterviewQ19View.as_view()), name="job-interview_q19"),
    path('job-interview/question-20', login_required(views.JobInterviewQ20View.as_view()), name="job-interview_q20"),
    path('job-interview/interview-success', login_required(views.InterviewSuccessView.as_view()), name="interview_success_view"),
    path('job-interview/interview-forfeited', login_required(views.InterviewForfeitView.as_view()), name="interview_forfeit_view"),
    path('job-interview/access-denied', login_required(views.JobInterviewAccessDenied.as_view()), name="interview_access_denied"),
]