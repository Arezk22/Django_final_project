from django import forms
from django.contrib.auth.models import User
from .models import Profile, Course, CourseDocument


class ExtendedRegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[("student", "Student"), ("teacher", "Teacher")],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Enrolled As",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user.profile.role = self.cleaned_data["role"]
            user.profile.save()
        return user


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "category", "level", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CourseDocumentForm(forms.ModelForm):
    class Meta:
        model = CourseDocument

        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:

            if not file.name.endswith((".pdf", ".txt")):
                raise forms.ValidationError("Only PDF and TXT files are allowed.")
        return file


# -------------------------------------------------profile form
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio"]

        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write something about yourself...",
                }
            )
        }
