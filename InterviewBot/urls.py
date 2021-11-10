"""InterviewBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from .router import router
from .views import(
    LoginViewAPI, 
    LogoutViewAPI,
    UpdateAccountViewAPI,
    AccountDetailsViewAPI,
    JobOfferingsListViewAPI,
    JobOfferingsDetailedViewAPI,
    SavedJobListViewAPI,
    SavedJobDetailedViewAPI,
    AppliedJobListViewAPI,
    AppliedJobDetailedUserViewAPI,
    AppliedJobDetailedAdminViewAPI,

    LoginView,
    password_reset_request
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('administrator/', include('administrator.urls', namespace='administrator')),
    path('user/', include('user.urls', namespace="user")),

    # API
    path('api/', include(router.urls)),
    path('api/login/', LoginViewAPI.as_view()),
    path('api/logout/', LogoutViewAPI.as_view()),
    path('api/update-account/', UpdateAccountViewAPI.as_view()),
    path('api/<email>/account-details/', AccountDetailsViewAPI.as_view()),
    path('api/job-offerings/', JobOfferingsListViewAPI.as_view()),
    path('api/<admin_id>/job-offerings/', JobOfferingsDetailedViewAPI.as_view()),
    path('api/saved-jobs/', SavedJobListViewAPI.as_view()),
    path('api/<user_id>/saved-jobs/', SavedJobDetailedViewAPI.as_view()),
    path('api/applied-jobs/', AppliedJobListViewAPI.as_view()),
    path('api/user/<user_id>/applied-jobs/', AppliedJobDetailedUserViewAPI.as_view()),
    path('api/job/<job_id>/applied-jobs/', AppliedJobDetailedAdminViewAPI.as_view()),

    # Login
    path('', LoginView.as_view(), name="login_view"),

    # Password Reset
    path('password_reset/', password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),  
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)