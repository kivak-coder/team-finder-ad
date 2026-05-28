from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, Project, Skill
from .forms import RegisterForm, LoginForm, EditProfileForm, ProjectForm, SkillForm
from django.contrib.auth.forms import PasswordChangeForm

# ----- helpers -----
def is_staff_user(user):
    return user.is_staff

# ----- auth views -----
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            return redirect('project_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('project_list')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('project_list')

# ----- project views -----
def project_list(request):
    projects = Project.objects.filter(status='open').order_by('-created_at')
    skill_filter = request.GET.get('skill')
    if skill_filter:
        # variant 1 does NOT require skill filtering – but we keep optional
        projects = projects.filter(skills__name__iexact=skill_filter)
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/project_list.html', {'projects': page_obj})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_participant = request.user.is_authenticated and request.user in project.participants.all()
    is_owner = request.user == project.owner
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'is_participant': is_participant,
        'is_owner': is_owner,
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/edit_project.html', {'form': form, 'project': project})

@login_required
def toggle_favorite(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)
    project = get_object_or_404(Project, pk=pk)
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({'status': 'ok', 'favorited': favorited})

@login_required
def favorite_projects(request):
    projects = request.user.favorites.all().order_by('-created_at')
    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    projects_page = paginator.get_page(page)
    return render(request, 'projects/favorite_projects.html', {'projects': projects_page})

@login_required
def join_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status != 'open':
        messages.error(request, "Project is closed")
        return redirect('project_detail', pk=pk)
    if request.user == project.owner:
        messages.error(request, "Owner cannot join own project")
        return redirect('project_detail', pk=pk)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        messages.success(request, "You left the project")
    else:
        project.participants.add(request.user)
        messages.success(request, "You joined the project")
    return redirect('project_detail', pk=pk)

@login_required
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    project.status = 'closed'
    project.save()
    return redirect('project_detail', pk=pk)

# ----- user profile views -----
def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    owned_projects = user_obj.owned_projects.filter(status='open').order_by('-created_at')
    return render(request, 'users/user_detail.html', {'profile_user': user_obj, 'owned_projects': owned_projects})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect('user_detail', pk=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed")
            return redirect('user_detail', pk=request.user.pk)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        skill, created = Skill.objects.get_or_create(name=skill_name.strip().lower())
        request.user.skills.add(skill)
        return JsonResponse({'status': 'ok', 'skill': skill.name})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def remove_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    request.user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})

# ----- user list with variant 1 filtering -----
def user_list(request):
    users = User.objects.filter(is_active=True).exclude(is_superuser=True).order_by('-date_joined')
    filter_type = request.GET.get('filter')
    if request.user.is_authenticated and filter_type:
        if filter_type == 'fav_authors':
            fav_projects = request.user.favorites.all()
            users = User.objects.filter(owned_projects__in=fav_projects).distinct()
        elif filter_type == 'my_participations_authors':
            my_participated = request.user.participated_projects.all()
            users = User.objects.filter(owned_projects__in=my_participated).distinct()
        elif filter_type == 'liked_my_projects':
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(favorites__in=my_projects).distinct()
        elif filter_type == 'participants_of_my_projects':
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(participated_projects__in=my_projects).distinct()
    paginator = Paginator(users, 12)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    return render(request, 'users/participants.html', {'users': users_page, 'current_filter': filter_type})

# ----- staff admin views -----
@user_passes_test(is_staff_user)
def staff_user_manage(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/staff_user_manage.html', {'users': users})

@user_passes_test(is_staff_user)
def staff_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect('staff_user_manage')

@user_passes_test(is_staff_user)
def staff_delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('staff_user_manage')

@user_passes_test(is_staff_user)
def staff_change_password(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        target_user.set_password(new_password)
        target_user.save()
        messages.success(request, f"Password changed for {target_user.email}")
        return redirect('staff_user_manage')
    return render(request, 'users/staff_change_password.html', {'target_user': target_user})

@user_passes_test(is_staff_user)
def staff_projects(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/staff_projects.html', {'projects': projects})

@user_passes_test(is_staff_user)
def staff_delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('staff_projects')