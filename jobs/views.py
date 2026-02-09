from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse
from .models import Job, Application, Category, Company, User, Subscription, SavedJob, HiddenJob, Course, CourseCategory, Enrollment, CourseModule, Lesson, Article, ArticleCategory, Message, Connection, UserProgress, Assignment, Submission
from .forms import ApplicantSignUpForm, EmployerSignUpForm, CollegeSignUpForm, ProfileEditForm, EducationFormSet, ExperienceFormSet, ApplicationForm, JobForm, CompanyForm
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

# ... existing views ...

class VerifiedInstitutionalUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin_user or self.request.user.verification_status == 'approved'
    
    def handle_no_permission(self):
        messages.warning(self.request, "Account pending verification. Access restricted.")
        if self.request.user.is_employer_user:
            return redirect('jobs:employer_dashboard')
        elif self.request.user.is_college_user:
            return redirect('jobs:college_dashboard')
        return redirect('jobs:home')

class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'jobs/company_form.html'
    success_url = reverse_lazy('jobs:employer_dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'jobs/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active (approved) jobs for this company
        context['jobs'] = Job.objects.filter(company=self.object, status='active', is_active=True).order_by('-created_at')
        return context

class EmployerDashboardView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/employer_dashboard.html'
    context_object_name = 'jobs'

    def get(self, request, *args, **kwargs):
        # Redirect to Company profile creation if not exists
        if request.user.user_type == 'employer':
            try:
                company = request.user.company
            except ObjectDoesNotExist:
                return redirect('jobs:company_create')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sub, created = Subscription.objects.get_or_create(user=self.request.user)
        context['subscription'] = sub
        return context

class JobCreateView(LoginRequiredMixin, VerifiedInstitutionalUserMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:employer_dashboard')

    def form_valid(self, form):
        form.instance.employer = self.request.user
        # Ensure user has a company
        if not hasattr(self.request.user, 'company'):
            messages.error(self.request, "You must create a company profile first.")
            return redirect('jobs:profile')
        form.instance.company = self.request.user.company
        form.instance.status = 'pending' # Default to pending
        return super().form_valid(form)

class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:employer_dashboard')
    slug_url_kwarg = 'slug'


    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('jobs:employer_dashboard')
    slug_url_kwarg = 'slug'


    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)

class EmployerJobApplicantsView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/applicants.html'
    context_object_name = 'job'
    slug_url_kwarg = 'slug'


    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check subscription
        sub, _ = Subscription.objects.get_or_create(user=self.request.user)
        context['subscription'] = sub
        context['subscription'] = sub
        context['applications'] = self.object.applications.all()
        return context

class EmployerKanbanView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/kanban_board.html'
    context_object_name = 'job'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group applications by status
        apps = self.object.applications.all()
        context['pending'] = apps.filter(status='pending')
        context['reviewing'] = apps.filter(status='reviewing')
        context['shortlisted'] = apps.filter(status='shortlisted')
        context['rejected'] = apps.filter(status='rejected')
        context['hired'] = apps.filter(status='hired')
        return context

def update_application_status(request, pk):
    if request.method == 'POST' and request.user.user_type == 'employer':
        import json
        data = json.loads(request.body)
        status = data.get('status')
        app = get_object_or_404(Application, pk=pk, job__employer=request.user)
        if status in ['pending', 'reviewing', 'shortlisted', 'rejected', 'hired']:
            app.status = status
            app.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

class PrivacyPolicyView(TemplateView):
    template_name = 'legal/privacy_policy.html'

class TermsOfServiceView(TemplateView):
    template_name = 'legal/terms_of_service.html'

class CommunityGuidelinesView(TemplateView):
    template_name = 'legal/terms_of_service.html' # Reuse or create specific if needed

# --- Admin Views ---

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'jobs/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_admin_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_jobs'] = Job.objects.filter(status='pending').order_by('-created_at')
        context['pending_employers'] = User.objects.filter(user_type='employer', verification_status='pending').order_by('-date_joined')
        context['pending_colleges'] = User.objects.filter(user_type='college', verification_status='pending').order_by('-date_joined')
        context['all_users'] = User.objects.all().order_by('-date_joined')[:50] # Show recent
        
        # Stats
        context['total_users'] = User.objects.count()
        context['total_jobs'] = Job.objects.count()
        context['total_courses'] = Course.objects.count()
        context['pending_courses'] = Course.objects.filter(status='pending').order_by('-created_at')
        context['pending_count'] = context['pending_jobs'].count() + context['pending_employers'].count() + context['pending_colleges'].count() + context['pending_courses'].count()
        return context

@login_required
@user_passes_test(lambda u: u.is_admin_user)
def verify_user(request, public_id, action):
    user = get_object_or_404(User, public_id=public_id)
    if action == 'approve':
        user.verification_status = 'approved'
        user.is_verified = True # Keep for compatibility
        messages.success(request, f"User {user.username} approved.")
    elif action == 'reject':
        user.verification_status = 'rejected'
        messages.warning(request, f"User {user.username} rejected.")
    user.save()
    return redirect('jobs:admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_admin_user)
def approve_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    job.status = 'active'
    job.save()
    messages.success(request, f"Job {job.title} approved.")
    return redirect('jobs:admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_admin_user)
def reject_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    job.status = 'rejected'
    job.save()
    messages.warning(request, f"Job {job.title} rejected.")
    return redirect('jobs:admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_admin_user)
def approve_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    course.status = 'active'
    course.save()
    messages.success(request, f"Course {course.title} approved.")
    return redirect('jobs:admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_admin_user)
def reject_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    course.status = 'rejected'
    course.save()
    messages.warning(request, f"Course {course.title} rejected.")
    return redirect('jobs:admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, public_id):
    user = get_object_or_404(User, public_id=public_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('jobs:admin_dashboard')

class AdminUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'jobs/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin_user

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        user_type = self.request.GET.get('type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_types'] = User.USER_TYPES
        return context

class AdminJobListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Job
    template_name = 'jobs/admin/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin_user

    def get_queryset(self):
        queryset = Job.objects.all().order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class AdminCourseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'jobs/admin/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin_user

    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class CollegeStudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Enrollment
    template_name = 'jobs/college/student_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_college_user

    def get_queryset(self):
        return Enrollment.objects.filter(course__college=self.request.user).select_related('student', 'course').order_by('-enrolled_at')

class EmployerApplicantListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Application
    template_name = 'jobs/employer/applicant_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_employer_user

    def get_queryset(self):
        return Application.objects.filter(job__employer=self.request.user).select_related('applicant', 'job').order_by('-created_at')


class HomeView(TemplateView):
    template_name = 'jobs/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_jobs'] = Job.objects.filter(status='active', is_active=True).order_by('-created_at')[:6]
        context['job_categories'] = Category.objects.all()
        context['article_categories'] = ArticleCategory.objects.all()[:8]
        
        if self.request.user.is_authenticated:
            # Suggestions logic
            user = self.request.user
            
            # Get IDs to exclude
            connections = Connection.objects.filter(
                (Q(sender=user) | Q(recipient=user))
            ).values_list('sender_id', 'recipient_id', 'status')
            
            exclude_ids = {user.id}
            for sender_id, recipient_id, status in connections:
                exclude_ids.add(sender_id)
                exclude_ids.add(recipient_id)
                
            context['suggested_connections'] = User.objects.filter(user_type='applicant').exclude(id__in=list(exclude_ids)).order_by('?')[:5]
        return context

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page = context['page_obj']
        if paginator:
            context['elided_page_range'] = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
        return context

    def get_queryset(self):
        queryset = Job.objects.filter(status='active', is_active=True).order_by('-created_at')
        
        # Exclude hidden jobs if user is authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(hidden_by_users__user=self.request.user)
            # Annotate saved status
            queryset = queryset.annotate(
                is_saved=Exists(SavedJob.objects.filter(job=OuterRef('pk'), user=self.request.user))
            )

        query = self.request.GET.get('q')
        location = self.request.GET.get('l')
        category = self.request.GET.get('category')
        
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if location:
            queryset = queryset.filter(location__icontains=location)
        if category:
            queryset = queryset.filter(category__id=category)
            
        return queryset

@login_required
def toggle_save_job(request, slug):
    if request.method == 'POST':
        job = get_object_or_404(Job, slug=slug)
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        if not created:
            saved_job.delete()
            saved = False
        else:
            saved = True
        return JsonResponse({'saved': saved})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def toggle_hide_job(request, slug):
    if request.method == 'POST':
        job = get_object_or_404(Job, slug=slug)
        HiddenJob.objects.get_or_create(user=request.user, job=job)
        return JsonResponse({'hidden': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin_user:
                return queryset
            if self.request.user.is_employer_user:
                # Employer can see their own jobs even if pending
                return queryset.filter(Q(status='active') | Q(employer=self.request.user))
        return queryset.filter(status='active', is_active=True)


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'jobs/apply.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(Job, slug=self.kwargs['slug'])
        # Check profile completeness
        user = self.request.user
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio']
        # Simple check: basic fields + having at least 1 education and 1 experience
        is_complete = all([getattr(user, field) for field in required_fields])
        # We can also check reverse relations if we want strictness, but let's stick to basic fields + CV for now.
        # Actually, CV is needed for "Profile Apply" effectively unless we generate one.
        has_cv = bool(user.cv)
        context['profile_complete'] = is_complete and has_cv
        return context

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        job = get_object_or_404(Job, slug=self.kwargs['slug'])
        form.instance.job = job

        
        # logical handling
        app_type = form.cleaned_data.get('application_type')
        if app_type == 'profile':
            # Verification already done in form.clean, but let's be double sure or handle specific logic
            if not self.request.user.cv:
                # Should not happen if validation works
                return self.form_invalid(form)
            form.instance.resume = self.request.user.cv
            form.instance.cover_letter = form.cleaned_data.get('cover_letter') or f"Applied with profile for {job.title}"
            
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('jobs:job_list')

class ApplicantSignUpView(CreateView):
    form_class = ApplicantSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return redirect('login')

class EmployerSignUpView(CreateView):
    form_class = EmployerSignUpForm
    template_name = 'registration/employer_signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return redirect('login')

class CollegeSignUpView(CreateView):
    form_class = CollegeSignUpForm
    template_name = 'registration/college_signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return redirect('login')

class CollegeDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'jobs/college_dashboard.html'
    context_object_name = 'courses'

    def test_func(self):
        return self.request.user.is_college_user

    def get_queryset(self):
        return Course.objects.filter(college=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get total students enrolled in all this college's courses
        enrollments = Enrollment.objects.filter(course__college=self.request.user)
        context['total_students'] = enrollments.values('student').distinct().count()
        context['pending_submissions'] = Submission.objects.filter(assignment__course__college=self.request.user, grade='').count()
        context['recent_enrollments'] = enrollments.order_by('-enrolled_at')[:10]
        return context

@login_required
@user_passes_test(lambda u: u.is_college_user)
def onboard_student(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        course_id = request.POST.get('course_id')
        try:
            student = User.objects.get(email=email, user_type='applicant')
            course = Course.objects.get(id=course_id, college=request.user)
            Enrollment.objects.get_or_create(student=student, course=course)
            messages.success(request, f"Student {student.get_full_name()} onboarded successfully.")
        except User.DoesNotExist:
            messages.error(request, "No student found with this email.")
        except Course.DoesNotExist:
            messages.error(request, "Invalid course selected.")
    return redirect('jobs:college_dashboard')

@login_required
def mark_lesson_complete(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    progress, created = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress.is_completed = True
    progress.save()
    
    # Try to find next lesson
    next_lesson = Lesson.objects.filter(
        module__course=lesson.module.course,
        order__gt=lesson.order
    ).first()
    
    if next_lesson:
        return redirect('jobs:lesson_detail', slug=next_lesson.slug)
    
    messages.success(request, f"Congratulations! You've completed {lesson.title}.")
    return redirect('jobs:course_detail', slug=lesson.module.course.slug)

class ApplicantDashboardView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'jobs/applicant_dashboard.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sent_requests'] = Connection.objects.filter(
            sender=self.request.user, status='pending'
        ).select_related('recipient')
        return context



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/profile.html'

class ResumeView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'jobs/resume_view.html'
    context_object_name = 'applicant'
    
    def get_object(self):
        # Allow viewing other users? For now, just self or maybe allowed users
        # If pk is provided, view that user, else self
        pk = self.kwargs.get('pk')
        if pk:
             # Add permission check here if needed
             return get_object_or_404(User, pk=pk)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context['education'] = user.education.all().order_by('-end_date')
        context['experience'] = user.experience.all().order_by('-end_date')
        # Format skills/languages if stored in fields (assuming bio or separate text)
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'jobs/profile_edit.html'
    success_url = reverse_lazy('jobs:profile')

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['education_formset'] = EducationFormSet(self.request.POST, instance=self.object)
            data['experience_formset'] = ExperienceFormSet(self.request.POST, instance=self.object)
        else:
            data['education_formset'] = EducationFormSet(instance=self.object)
            data['experience_formset'] = ExperienceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        education_formset = context['education_formset']
        experience_formset = context['experience_formset']
        if education_formset.is_valid() and experience_formset.is_valid():
            self.object = form.save()
            education_formset.instance = self.object
            education_formset.save()
            experience_formset.instance = self.object
            experience_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class NetworkView(TemplateView):
    template_name = 'jobs/network.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch data for the network page
        context['students'] = User.objects.filter(user_type='applicant').exclude(id=self.request.user.id if self.request.user.is_authenticated else -1)[:6]
        context['companies'] = Company.objects.all()[:6]
        context['colleges'] = User.objects.filter(user_type='college').exclude(id=self.request.user.id if self.request.user.is_authenticated else -1)[:6]
        return context

class MessagingView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/messaging.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all messages involving the user
        messages = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient', 'job', 'course').order_by('-timestamp')

        # Group by conversation
        conversations = {}
        for msg in messages:
            other_user = msg.recipient if msg.sender == user else msg.sender
            
            # Create a unique key for the conversation based on context
            if msg.job:
                key = f"job_{msg.job.id}_{other_user.id}"
                type_ = 'job'
                context_title = msg.job.title
                priority = 1
            elif msg.course:
                key = f"course_{msg.course.id}_{other_user.id}"
                type_ = 'course'
                context_title = msg.course.title
                priority = 2
            else:
                key = f"direct_{other_user.id}"
                type_ = 'direct'
                context_title = "Direct Message"
                priority = 3

            if key not in conversations:
                conversations[key] = {
                    'other_user': other_user,
                    'last_message': msg,
                    'type': type_,
                    'context_title': context_title,
                    'priority': priority,
                    'messages': [],
                    'job_id': msg.job.id if msg.job else None,
                    'course_id': msg.course.id if msg.course else None
                }
            conversations[key]['messages'].append(msg)

        # Sort conversations by priority (Job > Course > Direct) then by timestamp
        sorted_conversations = sorted(
            conversations.values(), 
            key=lambda x: (x['priority'], -x['last_message'].timestamp.timestamp())
        )

        context['conversations'] = sorted_conversations
        return context

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        job_id = request.POST.get('job_id')
        course_id = request.POST.get('course_id')
        
        if not recipient_id or not content:
            return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)

        recipient = get_object_or_404(User, id=recipient_id)
        job = get_object_or_404(Job, id=job_id) if job_id else None
        course = get_object_or_404(Course, id=course_id) if course_id else None

        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            job=job,
            course=course
        )

        return JsonResponse({
            'status': 'success',
            'message': {
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
                'sender': msg.sender.username
            }
        })
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    results = []
    for user in users:
        results.append({
            'id': user.id,
            'username': user.username,
            'name': user.get_full_name() or user.username,
            'profile_picture': user.profile_picture.url if user.profile_picture else None
        })
    
    return JsonResponse(results, safe=False)

class NetworkView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/network.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Connections
        connections = Connection.objects.filter(
            (Q(sender=user) | Q(recipient=user)) & Q(status='accepted')
        ).select_related('sender', 'recipient')
        
        # Incoming Requests
        received_requests = Connection.objects.filter(
            recipient=user, status='pending'
        ).select_related('sender')

        # Sent Requests (for display and exclusion)
        sent_requests = Connection.objects.filter(
            sender=user, status='pending'
        ).select_related('recipient')
        
        sent_requests_ids = sent_requests.values_list('recipient_id', flat=True)
        
        # Received Requests IDs (to exclude from suggestions)
        received_requests_ids = received_requests.values_list('sender_id', flat=True)

        # Exclude IDs
        connected_ids = set()
        for c in connections:
            connected_ids.add(c.sender.id)
            connected_ids.add(c.recipient.id)
        
        exclude_ids = connected_ids.union(set(sent_requests_ids))
        exclude_ids = exclude_ids.union(set(received_requests_ids))
        exclude_ids.add(user.id)
        
        # Suggestions (Simple logic: excluding connected/pending)
        # Explicitly cast to list to ensure compatibility
        context['suggested_users'] = User.objects.exclude(id__in=list(exclude_ids))[:6]
        context['received_requests'] = received_requests
        context['sent_requests'] = sent_requests
        context['my_network_count'] = len(connected_ids) - 1 if user.id in connected_ids else len(connected_ids)
        
        return context

@login_required
def send_connection_request(request, user_id):
    if request.method == 'POST':
        recipient = get_object_or_404(User, id=user_id)
        if recipient == request.user:
            return JsonResponse({'status': 'error', 'message': 'Cannot connect to self'}, status=400)
            
        # Check if already connected or pending
        existing = Connection.objects.filter(
            (Q(sender=request.user, recipient=recipient) | Q(sender=recipient, recipient=request.user))
        ).first()

        if existing:
             if existing.status == 'accepted':
                 return JsonResponse({'status': 'error', 'message': 'Already connected'})
             if existing.status == 'pending':
                 return JsonResponse({'status': 'error', 'message': 'Request already pending'})
        
        Connection.objects.create(sender=request.user, recipient=recipient, status='pending')
        return JsonResponse({'status': 'success', 'message': 'Request sent'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def update_connection_status(request, pk, action):
    if request.method == 'POST':
        connection = get_object_or_404(Connection, id=pk, recipient=request.user, status='pending')
        
        if action == 'accept':
            connection.status = 'accepted'
            connection.save()
            return JsonResponse({'status': 'success', 'message': 'Request accepted'})
        elif action == 'reject':
            connection.status = 'rejected'
            connection.save()
            return JsonResponse({'status': 'success', 'message': 'Request rejected'})
            
@login_required
def update_connection_status(request, pk, action):
    if request.method == 'POST':
        connection = get_object_or_404(Connection, id=pk, recipient=request.user, status='pending')
        
        if action == 'accept':
            connection.status = 'accepted'
            connection.save()
            return JsonResponse({'status': 'success', 'message': 'Request accepted'})
        elif action == 'reject':
            connection.status = 'rejected'
            connection.save()
            return JsonResponse({'status': 'success', 'message': 'Request rejected'})
            
    return JsonResponse({'status': 'error'}, status=405)

class NotificationsView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/notifications.html'

class LearnView(ListView):
    model = Course
    template_name = 'jobs/learn.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='active').order_by('-rating')
        category_slug = self.request.GET.get('category')
        if category_slug:
            # Filter by category or subcategory
            queryset = queryset.filter(Q(category__slug=category_slug) | Q(category__parent__slug=category_slug))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get only parent categories for the filter sidebar
        context['parent_categories'] = CourseCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
        context['current_category'] = self.request.GET.get('category')
        # Dynamic stats
        if self.request.user.is_authenticated:
            context['certificates_count'] = Enrollment.objects.filter(student=self.request.user, status='completed').count()
        else:
            context['certificates_count'] = 0
            
        paginator = context['paginator']
        page = context['page_obj']
        if paginator:
            context['elided_page_range'] = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
            
        return context

class StudentDashboardView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'jobs/student_dashboard.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course').prefetch_related('course__modules__lessons')

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'jobs/course_detail.html'
    context_object_name = 'course'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin_user:
                return queryset
            if self.request.user.is_college_user:
                return queryset.filter(Q(status='active') | Q(college=self.request.user))
        return queryset.filter(status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user is enrolled
        context['is_enrolled'] = Enrollment.objects.filter(student=self.request.user, course=self.object).exists()
        # Get syllabus (modules and lessons)
        context['modules'] = self.object.modules.all().prefetch_related('lessons')
        return context

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'jobs/lesson_detail.html'
    context_object_name = 'lesson'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object.module.course
        # Check if user is enrolled to view full content
        is_enrolled = Enrollment.objects.filter(student=self.request.user, course=course).exists()
        context['is_enrolled'] = is_enrolled
        context['course'] = course
        context['all_modules'] = course.modules.all().prefetch_related('lessons')
        
        # Next/Prev Lesson logic
        all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))
        current_index = all_lessons.index(self.object) if self.object in all_lessons else -1
        
        if current_index != -1:
            if current_index > 0:
                context['prev_lesson'] = all_lessons[current_index - 1]
            if current_index < len(all_lessons) - 1:
                context['next_lesson'] = all_lessons[current_index + 1]
                
        # Progress check
        context['is_completed'] = UserProgress.objects.filter(user=self.request.user, lesson=self.object, is_completed=True).exists()
        return context

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        course.students_enrolled += 1
        course.save()
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, "You are already enrolled in this course.")
    return redirect('jobs:course_detail', slug=course.slug)

class CourseCreateView(LoginRequiredMixin, VerifiedInstitutionalUserMixin, CreateView):
    model = Course
    fields = ['title', 'category', 'description', 'duration', 'fees', 'level', 'image']
    template_name = 'jobs/course_form.html'
    success_url = reverse_lazy('jobs:college_dashboard')

    def form_valid(self, form):
        form.instance.college = self.request.user
        return super().form_valid(form)

class ArticleListView(ListView):
    model = Article
    template_name = 'jobs/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        queryset = Article.objects.select_related('category', 'author').order_by('-created_at')
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(Q(category__slug=category_slug) | Q(category__parent__slug=category_slug))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ArticleCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
        context['current_category'] = self.request.GET.get('category')
        
        paginator = context['paginator']
        page = context['page_obj']
        if paginator:
            context['elided_page_range'] = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
            
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'jobs/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

class PrivacyView(TemplateView):
    template_name = 'jobs/privacy.html'

class TermsView(TemplateView):
    template_name = 'jobs/terms.html'

class GuidelinesView(TemplateView):
    template_name = 'jobs/guidelines.html'
