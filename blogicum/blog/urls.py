from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostCreateView.as_view(), name='create_post'),
    path("profile/<str:username>/edit/", views.ProfileUpdateView.as_view(),name="edit_profile"),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('comment/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('index/', views.Index.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
