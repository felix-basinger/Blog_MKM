from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('user/<str:username>', views.UserPostListView.as_view(), name='user-posts'),
    path('about/', views.about, name='about'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like/', views.like_post, name='like-post'),
    path('popular/', views.PopularPostListView.as_view(), name='popular-posts'),
    path('liked/', views.LikedPostsListView.as_view(), name='liked-posts'),
    path('dislike/<int:pk>/', views.dislike_post, name='dislike-post'),
    path('tag/<str:tag>/', views.TagPostListView.as_view(), name='tag-posts'),
    path('delete_tag/<int:tag_id>/', views.delete_tag, name='delete-tag'),
]
