# decorators.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def donor_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'donor'):
            return view_func(request, *args, **kwargs)
        return render(request, 'access-denied.html', status=403)
    return _wrapped_view

def hcworker_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'hcworker'):
            return view_func(request, *args, **kwargs)
        return render(request, 'access-denied.html', status=403)
    return _wrapped_view


def hcworker_admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'hcworker') and request.user.hcworker.role == 'admin':
            return view_func(request, *args, **kwargs)
        return render(request, 'access-denied.html', status=403)
    return _wrapped_view


def bbworker_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'bbworker'):
            return view_func(request, *args, **kwargs)
        return render(request, 'access-denied.html', status=403)
    return _wrapped_view

def bbworker_admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'bbworker') and request.user.bbworker.role == 'admin':
            return view_func(request, *args, **kwargs)
        return render(request, 'access-denied.html', status=403)
    return _wrapped_view