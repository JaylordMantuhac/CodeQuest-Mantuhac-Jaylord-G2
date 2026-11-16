from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Challenge, Submission
from .forms import ChallengeForm, SubmissionForm
from accounts.decorators import role_required


@login_required
def challenge_list(request):
    challenges = Challenge.objects.all().order_by('-created_at')
    return render(request, 'challenges/challenge_list.html', {'challenges': challenges})


@login_required
def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    user_submissions = None
    form = None

    if request.user.role == 'student':
        user_submissions = Submission.objects.filter(challenge=challenge, student=request.user)
        form = SubmissionForm()

    return render(request, 'challenges/challenge_detail.html', {
        'challenge': challenge,
        'form': form,
        'user_submissions': user_submissions,
    })


@login_required
def challenge_submit(request, pk):
    if request.user.role != 'student':
        messages.error(request, 'Only students can submit answers.')
        return redirect('challenge_detail', pk=pk)

    challenge = get_object_or_404(Challenge, pk=pk)

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.challenge = challenge
            submission.student = request.user
            user_answer = submission.answer.strip()
            expected = challenge.expected_output.strip()
            submission.is_correct = (user_answer == expected)
            submission.save()

            if submission.is_correct:
                messages.success(request, 'Correct! Well done.')
            else:
                messages.error(request, 'Not quite right. Try again.')

            return redirect('challenge_detail', pk=pk)
    else:
        form = SubmissionForm()

    return render(request, 'challenges/challenge_detail.html', {
        'challenge': challenge,
        'form': form,
    })


@role_required(['admin'])
def challenge_create(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.created_by = request.user
            challenge.save()
            messages.success(request, 'Challenge created.')
            return redirect('challenge_list')
    else:
        form = ChallengeForm()

    return render(request, 'challenges/challenge_form.html', {'form': form, 'action': 'Create'})


@role_required(['admin'])
def challenge_edit(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Challenge updated.')
            return redirect('challenge_detail', pk=pk)
    else:
        form = ChallengeForm(instance=challenge)

    return render(request, 'challenges/challenge_form.html', {'form': form, 'action': 'Edit', 'challenge': challenge})


@role_required(['admin'])
def challenge_delete(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.method == 'POST':
        challenge.delete()
        messages.success(request, 'Challenge deleted.')
        return redirect('challenge_list')

    return render(request, 'challenges/challenge_confirm_delete.html', {'challenge': challenge})


@login_required
def my_submissions(request):
    if request.user.role != 'student':
        messages.error(request, 'This page is for students only.')
        return redirect('challenge_list')

    submissions = Submission.objects.filter(student=request.user).select_related('challenge')
    return render(request, 'challenges/my_submissions.html', {'submissions': submissions})
