from django import forms
from django.contrib.auth.models import User
from .models import Profile

class ExtendedRegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Enrolled As"
    )
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # encrypt Password
        if commit:
            user.save() 
            
            user_profile = user.profile
            user_profile.role = self.cleaned_data['role']
            user_profile.save()
            
        return user