from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from team_finder.constants import (
    PROJECTS_PER_PAGE,
)


def paginate_queryset(request, queryset, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj
