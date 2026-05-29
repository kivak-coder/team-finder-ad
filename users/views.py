from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate_queryset
from team_finder.constants import USERS_PER_PAGE
from .forms import (
    ChangePasswordForm,
    LoginForm,
    ProfileEditForm,
    RegistrationForm,
)
from .models import User


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:project_list')
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('projects:project_list')
    return render(request, 'users/login.html', {'form': form, 'from': form})


def logout_view(request):
    logout(request)
    return redirect('projects:project_list')


def user_list_view(request):
    users_qs = User.objects.all().order_by('-id')
    active_filter = request.GET.get('filter')
    
    if request.user.is_authenticated and active_filter:
        if active_filter == 'owners-of-favorite-projects':
            users_qs = User.objects.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif active_filter == 'owners-of-participating-projects':
            users_qs = User.objects.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()
        elif active_filter == 'interested-in-my-projects':
            users_qs = User.objects.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()
        elif active_filter == 'participants-of-my-projects':
            users_qs = User.objects.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    page_obj = paginate_queryset(request, users_qs, per_page=USERS_PER_PAGE)

    context = {
        'page_obj': page_obj,
        'active_filter': active_filter,
        'query_prefix': f'filter={active_filter}&' if active_filter else '',
        'participants': page_obj,
        'active_skill': active_filter,
    }
    return render(request, 'users/participants.html', context)


def user_detail_view(request, pk):
    return render(
        request,
        'users/user-details.html',
        {'user': get_object_or_404(User, pk=pk)}
    )


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect('users:user_detail', pk=request.user.pk)
    return render(
        request,
        'users/edit_profile.html',
        {'form': form, 'from': form}
    )


@login_required
def change_password_view(request):
    form = ChangePasswordForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        update_session_auth_hash(request, form.save())
        return redirect('users:user_detail', pk=request.user.pk)
    return render(
        request,
        'users/change_password.html',
        {'form': form, 'from': form}
    )