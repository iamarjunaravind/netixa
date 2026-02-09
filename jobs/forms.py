from django import forms
from .models import User, Application, Job, Company, Company

# ... (imports)

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'location', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'description', 'location', 'job_type', 'salary_range']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ApplicantSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), label="Place", required=False)
    terms_accepted = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'job_role', 'address', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'applicant'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EmployerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    terms_accepted = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employer'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CollegeSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    terms_accepted = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'college'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'profile_picture', 'job_role', 'current_position',
            'age', 'dob', 'address', 'bio', 'cv'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

from django.forms import inlineformset_factory
from .models import Education, Experience

EducationFormSet = inlineformset_factory(
    User, Education, 
    fields=['course', 'college', 'start_date', 'end_date'], 
    extra=1, can_delete=True,
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
    }
)



ExperienceFormSet = inlineformset_factory(
    User, Experience, 
    fields=['title', 'company', 'start_date', 'end_date'], 
    extra=1, can_delete=True,
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
    }
)

class ApplicationForm(forms.ModelForm):
    APPLICATION_TYPES = [
        ('profile', 'Apply with Profile'),
        ('upload', 'Upload Resume')
    ]
    
    application_type = forms.ChoiceField(
        choices=APPLICATION_TYPES, 
        widget=forms.RadioSelect,
        initial='upload'
    )
    
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us why you are a good fit...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['resume'].required = False

    def clean(self):
        cleaned_data = super().clean()
        app_type = cleaned_data.get('application_type')
        resume = cleaned_data.get('resume')

        if app_type == 'upload' and not resume:
            self.add_error('resume', 'Please upload your resume.')
        
        if app_type == 'profile':
            if not self.user or not self.user.cv:
                # This fallback might be caught earlier in the view, but good for safety
                self.add_error('application_type', 'Your profile does not have a CV attached. Please upload one or edit your profile.')
            # We will handle assigning the profile CV in the view/save method
            
        return cleaned_data

