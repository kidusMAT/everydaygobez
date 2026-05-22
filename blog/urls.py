from django.urls import path
from . import views

urlpatterns = [
    # Auth paths
    path('login/', views.auth_login, name='login'),
    path('logout/', views.auth_logout, name='logout'),
    path('register/', views.auth_register, name='register'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/edit/code/', views.profile_code_editor, name='profile_code_editor'),
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),

    # Blog paths
    path('', views.post_list, name='post_list'),
    path('category/<slug:category_slug>/', views.post_list, name='category_filter'),
    path('author/<str:username>/', views.author_feed, name='author_feed'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('contact/', views.contact_us, name='contact_us'),
]
