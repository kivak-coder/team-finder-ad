from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from team_finder.constants import (
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    PROJECTS_PER_PAGE,
)
from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    projects_qs = (
        Project.objects
        .select_related('owner')
        .prefetch_related('participants')
        .all()
        .order_by('-created_at')
    )

    page_obj = paginate_queryset(
        request,
        projects_qs,
        per_page=PROJECTS_PER_PAGE
    )

    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': projects_qs,
        'query_prefix': '',
    })


@login_required
def favorites_view(request):
    fav_qs = (
        request.user.favorites
        .select_related('owner')
        .prefetch_related('participants')
        .all()
        .order_by('-created_at')
    )

    page_obj = paginate_queryset(
        request,
        fav_qs,
        per_page=PROJECTS_PER_PAGE
    )

    return render(request, 'projects/favorite_projects.html', {
        'page_obj': page_obj,
        'projects': fav_qs,
        'query_prefix': '',
    })


def project_detail_view(request, pk):
    return render(
        request,
        'projects/project-details.html',
        {'project': get_object_or_404(Project, pk=pk)}
    )


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:project_detail', pk=project.pk)

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        return redirect('projects:project_detail', pk=project.pk)

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True}
    )


@login_required
@require_POST
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user == project.owner and project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({
            'status': 'ok', 
            'project_status': PROJECT_STATUS_CLOSED
        })

    return JsonResponse(
        {'status': 'error'},
        status=HTTPStatus.FORBIDDEN
    )


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_fav = request.user.favorites.filter(id=project.id).exists()
    if is_fav:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse({'status': 'ok', 'favorited': not is_fav})


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    is_part = project.participants.filter(id=request.user.id).exists()

    if is_part:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({
        'status': 'ok',
        'participated': not is_part,
        'participant': not is_part
    })
