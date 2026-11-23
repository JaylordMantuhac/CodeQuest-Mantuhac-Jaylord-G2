from django import forms
from .models import Challenge, Submission


class ChallengeForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        error_messages={'required': 'Title is required.'},
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    expected_output = forms.CharField(
        required=True,
        error_messages={'required': 'Expected output is required.'},
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
    )

    class Meta:
        model = Challenge
        fields = ['title', 'description', 'category', 'difficulty', 'language', 'expected_output']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Title is required.')
        return title

    def clean_expected_output(self):
        output = self.cleaned_data.get('expected_output', '').strip()
        if not output:
            raise forms.ValidationError('Expected output is required.')
        return output

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise forms.ValidationError('Description is required.')
        return description


class SubmissionForm(forms.ModelForm):
    answer = forms.CharField(
        required=True,
        error_messages={'required': 'Answer cannot be empty.'},
        widget=forms.Textarea(attrs={
            'rows': 6,
            'class': 'form-control',
            'placeholder': 'Type your answer here...',
        }),
    )

    class Meta:
        model = Submission
        fields = ['answer']

    def clean_answer(self):
        answer = self.cleaned_data.get('answer', '').strip()
        if not answer:
            raise forms.ValidationError('Answer cannot be empty.')
        return answer
