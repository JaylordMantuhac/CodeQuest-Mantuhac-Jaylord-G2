from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Profile
from .forms import RegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from .decorators import role_required

try:
    from challenges.models import Challenge, Submission
    CHALLENGES_APP = True
except ImportError:
    CHALLENGES_APP = False


def index_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    return render(request, 'accounts/landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Welcome to CodeQuest, {user.first_name}! Your account has been created successfully. Please log in."
            )
            return redirect('accounts:login')
        else:
            messages.error(
                request,
                "Registration failed. Please check the form errors below and try again."
            )
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']

            lookup_username = credential
            user_by_email = User.objects.filter(email__iexact=credential).first()
            if user_by_email:
                lookup_username = user_by_email.username

            user = authenticate(request, username=lookup_username, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(
                        request,
                        f"Welcome back, {user.first_name or user.username}! You are logged in as {user.get_role_display_name()}."
                    )
                    next_url = request.GET.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('accounts:dashboard_redirect')
                else:
                    messages.error(request, "This account is inactive. Please contact support.")
            else:
                messages.error(
                    request,
                    "Invalid username/email or password. Please check your credentials and try again."
                )
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    username = request.user.username
    auth_logout(request)
    messages.info(request, f"Goodbye {username}! You have been logged out securely.")
    return redirect('accounts:login')


@login_required
def dashboard_redirect_view(request):
    if request.user.role == User.ROLE_ADMIN or request.user.is_staff or request.user.is_superuser:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:student_dashboard')


@login_required
@role_required([User.ROLE_ADMIN])
def admin_dashboard_view(request):
    total_users = User.objects.count()
    student_count = User.objects.filter(role=User.ROLE_STUDENT).count()
    admin_count = User.objects.filter(role=User.ROLE_ADMIN).count()
    recent_users = User.objects.order_by('-date_joined')[:6]

    total_challenges = Challenge.objects.count() if CHALLENGES_APP else 0
    total_submissions = Submission.objects.count() if CHALLENGES_APP else 0

    context = {
        'total_users': total_users,
        'student_count': student_count,
        'admin_count': admin_count,
        'recent_users': recent_users,
        'role_title': 'Quest Master / Administrator',
        'total_challenges': total_challenges,
        'total_submissions': total_submissions,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
@role_required([User.ROLE_STUDENT])
def student_dashboard_view(request):
    total_challenges = Challenge.objects.count() if CHALLENGES_APP else 0
    my_submissions = Submission.objects.filter(student=request.user) if CHALLENGES_APP else []
    correct_count = sum(1 for s in my_submissions if s.is_correct) if CHALLENGES_APP else 0

    context = {
        'role_title': 'Quest Adventurer / Student',
        'total_challenges': total_challenges,
        'my_submission_count': len(list(my_submissions)),
        'correct_count': correct_count,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = Profile.objects.create(user=request.user)

    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below and try saving again.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)
