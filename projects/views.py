from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Project
from .forms import ProjectForm

def project_list_view(request):
    projects_qs = Project.objects.all().order_by('-created_at')
    paginator = Paginator(projects_qs, 12)
    page = request.GET.get('page')
    try: 
        page_obj = paginator.page(page)
    except PageNotAnInteger: 
        page_obj = paginator.page(1)
    except EmptyPage: 
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': projects_qs, 
        'query_prefix': '', # Нужен для ссылок пагинации в шаблоне
    })

@login_required
def favorites_view(request):
    fav_qs = request.user.favorites.all().order_by('-created_at')
    
    paginator = Paginator(fav_qs, 12)
    page = request.GET.get('page')
    
    try: 
        page_obj = paginator.page(page)
    except PageNotAnInteger: 
        page_obj = paginator.page(1)
    except EmptyPage: 
        page_obj = paginator.page(paginator.num_pages)
        
    return render(request, 'projects/favorite_projects.html', {
        'page_obj': page_obj,
        'projects': fav_qs,
        'query_prefix': '',
    })

def project_detail_view(request, pk):
    return render(request, 'projects/project-details.html', {'project': get_object_or_404(Project, pk=pk)})

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user) # Автор автоматически участник
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})

@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})

@login_required
@require_POST
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.owner and project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})
    return JsonResponse({'status': 'error'}, status=403)

@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        is_fav = False
    else:
        request.user.favorites.add(project)
        is_fav = True
    return JsonResponse({'status': 'ok', 'favorited': is_fav})

@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_part = False
    else:
        project.participants.add(request.user)
        is_part = True
        
    return JsonResponse({
        'status': 'ok', 
        'participated': is_part, 
        'participant': is_part
    })
