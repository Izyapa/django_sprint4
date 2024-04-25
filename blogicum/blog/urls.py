"""Импорт модулей."""
from django.urls import path, include

from . import views

app_name = 'blog'

post_detail_patterns = [
    path('', views.PostDetailView.as_view(), name='post_detail'),
    path('edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('edit_comment/<int:comment_id>/', views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('comment/', views.CommentCreateView.as_view(), name='add_comment'),
]

post_urls = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:post_id>/', include(post_detail_patterns))
]

urlpatterns = [
    path('profile/', include([
        path('edit/', views.ProfileUpdateView.as_view(),
             name='edit_profile'),
        path('<str:username>/', views.ProfileDetailView.as_view(),
             name='profile'),
    ])),
    path('category/<slug:category_slug>/', views.CategoryList.as_view(),
         name='category_posts'),
    path('posts/', include(post_urls)),
    path('', views.Index.as_view(), name='index')
]
