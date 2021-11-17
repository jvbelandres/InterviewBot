from django.contrib.auth.decorators import login_required

from django.urls import path
from . import views

#path arranged alphabetically by name
app_name= 'administrator'
urlpatterns=[
    #path('api/data', views.get_data, name='api-data'),

    #TEST URL
    path('dashboard/', login_required(views.DashboardView.as_view()), name="dashboard_view"),
    path('job-lists/', login_required(views.JobListsView.as_view()), name="job-lists_view"),
    path('create-job-one/', login_required(views.CreateJobOneView.as_view()), name="create-job-one_view"),
    path('create-job-questions/', login_required(views.CreateJobQuestionsView.as_view()), name="create-job-questions_view"),
    path('create-admin/', login_required(views.AdminRegistrationView.as_view()), name="create-admin_view"),
    path('create-staff/', login_required(views.StaffRegistrationView.as_view()), name="create-staff_view"),
    path('registration/complete/', views.RegisterComplete.as_view(), name="registration_complete"),
    path('activate/<uidb64>/<token>/', views.sp_activate, name="sp_activate"),
    path('activate/success/', views.SpActivationSuccess.as_view(), name="activate-success"),
    path('activate/failed/', views.SpActivationFailed.as_view(), name="activate-failed"),
    path('settings/', login_required(views.SettingsView.as_view()), name="settings_view"),
    path('applicants/',login_required(views.Applicants.as_view()), name="applicants_view"),
    path('applicant/response', login_required(views.ResponseView.as_view()), name="response_view"),
    path('logout/', login_required(views.LogOutView.as_view()), name="logout_view"),
    path('denied/', login_required(views.AdminAccessDeniedView.as_view()), name="access_denied_view"),
]