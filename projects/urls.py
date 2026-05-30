from django.urls import path

from . import views

app_name = 'projects'
urlpatterns = [
    path('list/', views.project_list_view, name='project_list'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('create-project/', views.create_project_view, name='create_project'),
    path('<int:pk>/', views.project_detail_view, name='project_detail'),
    path('<int:pk>/edit/', views.edit_project_view, name='edit_project'),
    path('<int:pk>/complete/', views.complete_project_view,
         name='complete_project'),
    path('<int:pk>/toggle-favorite/', views.toggle_favorite_view,
         name='toggle_favorite'),
    path('<int:pk>/toggle-participate/', views.toggle_participate_view,
         name='toggle_participate'),
]
