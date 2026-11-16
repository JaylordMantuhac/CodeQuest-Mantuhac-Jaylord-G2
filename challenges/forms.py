from django import forms
from .models import Challenge, Submission


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'category', 'difficulty', 'language', 'expected_output']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'expected_output': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
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
