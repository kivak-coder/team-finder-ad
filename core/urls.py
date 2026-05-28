from django.urls import path
from . import views

urlpatterns = [
    path('projects/list/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create-project/', views.create_project, name='create_project'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('projects/<int:pk>/join/', views.join_project, name='join_project'),
    path('projects/<int:pk>/complete/', views.complete_project, name='complete_project'),
    path('projects/favorites/', views.favorite_projects, name='favorite_projects'),
    path('users/register/', views.register_view, name='register'),
    path('users/login/', views.login_view, name='login'),
    path('users/logout/', views.logout_view, name='logout'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/edit/', views.edit_profile, name='edit_profile'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('users/list/', views.user_list, name='user_list'),
    path('users/add-skill/', views.add_skill, name='add_skill'),
    path('users/remove-skill/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    # staff
    path('staff/users/', views.staff_user_manage, name='staff_user_manage'),
    path('staff/users/<int:pk>/toggle/', views.staff_toggle_active, name='staff_toggle_active'),
    path('staff/users/<int:pk>/delete/', views.staff_delete_user, name='staff_delete_user'),
    path('staff/users/<int:pk>/change-password/', views.staff_change_password, name='staff_change_password'),
    path('staff/projects/', views.staff_projects, name='staff_projects'),
    path('staff/projects/<int:pk>/delete/', views.staff_delete_project, name='staff_delete_project'),
]
