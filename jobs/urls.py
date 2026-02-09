from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('job/<slug:slug>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/<slug:slug>/apply/', views.ApplicationCreateView.as_view(), name='apply'),
    path('dashboard/applicant/', views.ApplicantDashboardView.as_view(), name='applicant_dashboard'),
    path('dashboard/employer/', views.EmployerDashboardView.as_view(), name='employer_dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('resume/<int:pk>/', views.ResumeView.as_view(), name='resume_view'),
    
    # College
    path('college/signup/', views.CollegeSignUpView.as_view(), name='college_signup'),
    path('college/dashboard/', views.CollegeDashboardView.as_view(), name='college_dashboard'),
    path('college/course/new/', views.CourseCreateView.as_view(), name='course_create'),
    path('college/onboard-student/', views.onboard_student, name='onboard_student'),

    # Learn / Education
    path('learn/', views.LearnView.as_view(), name='learn'),
    path('learn/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('learn/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('learn/<slug:slug>/enroll/', views.enroll_course, name='course_enroll'),
    path('learn/<slug:slug>/enroll/', views.enroll_course, name='course_enroll'),
    path('learn/lesson/<slug:slug>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('learn/lesson/<slug:slug>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),

    # Articles
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),

    path('company/new/', views.CompanyCreateView.as_view(), name='company_create'),
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    
    # Employer URLs
    path('job/new/', views.JobCreateView.as_view(), name='job_create'),
    path('job/<slug:slug>/edit/', views.JobUpdateView.as_view(), name='job_update'),
    path('job/<slug:slug>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('job/<slug:slug>/applicants/', views.EmployerJobApplicantsView.as_view(), name='job_applicants'),
    path('job/<slug:slug>/applicants/', views.EmployerJobApplicantsView.as_view(), name='job_applicants'),
    path('job/<slug:slug>/kanban/', views.EmployerKanbanView.as_view(), name='job_kanban'),
    path('job/application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    
    # Legal
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    path('guidelines/', views.CommunityGuidelinesView.as_view(), name='guidelines'),
    
    # Admin URLs
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('user/<str:public_id>/verify/<str:action>/', views.verify_user, name='verify_user'),
    path('user/<str:public_id>/delete/', views.delete_user, name='delete_user'),
    path('admin-dashboard/job/<slug:slug>/approve/', views.approve_job, name='approve_job'),
    path('admin-dashboard/job/<slug:slug>/reject/', views.reject_job, name='reject_job'),
    path('admin-dashboard/course/<slug:slug>/approve/', views.approve_course, name='approve_course'),
    path('admin-dashboard/course/<slug:slug>/reject/', views.reject_course, name='reject_course'),
    
    # New Functional Dashboard Lists
    path('admin-dashboard/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin-dashboard/jobs/', views.AdminJobListView.as_view(), name='admin_job_list'),
    path('admin-dashboard/courses/', views.AdminCourseListView.as_view(), name='admin_course_list'),
    path('college/students/', views.CollegeStudentListView.as_view(), name='college_student_list'),
    path('employer/applicants/', views.EmployerApplicantListView.as_view(), name='employer_applicant_list'),

    # Action URLs
    path('job/<slug:slug>/toggle-save/', views.toggle_save_job, name='toggle_save_job'),
    path('job/<slug:slug>/toggle-hide/', views.toggle_hide_job, name='toggle_hide_job'),

    # New Pages
    path('network/', views.NetworkView.as_view(), name='network'),
    path('network/connect/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
    path('network/status/<int:pk>/<str:action>/', views.update_connection_status, name='update_connection_status'),
    path('messaging/', views.MessagingView.as_view(), name='messaging'),
    path('messaging/send/', views.send_message, name='send_message'),
    path('messaging/search-users/', views.search_users, name='search_users'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('learn/', views.LearnView.as_view(), name='learn'),
    
    # Legal
    path('p/privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('p/terms/', views.TermsView.as_view(), name='terms'),
    path('p/guidelines/', views.GuidelinesView.as_view(), name='guidelines'),
]
