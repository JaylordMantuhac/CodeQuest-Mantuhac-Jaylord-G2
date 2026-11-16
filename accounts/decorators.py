from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')

            user_role = getattr(request.user, 'role', None)

            if 'admin' in allowed_roles and (request.user.is_superuser or request.user.is_staff):
                return view_func(request, *args, **kwargs)

            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f"Access Denied: Your role ({request.user.get_role_display_name()}) is not authorized to view that dashboard."
                )
                if user_role == 'admin':
                    return redirect('accounts:admin_dashboard')
                elif user_role == 'student':
                    return redirect('accounts:student_dashboard')
                else:
                    return redirect('accounts:login')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
