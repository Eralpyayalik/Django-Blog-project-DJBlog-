from django.contrib import admin
from django.urls import path
from.import views
app_name="article"
urlpatterns = [
    path("dashboard/",views.dashboard,name="dashboard"),
    path("addarticle/",views.addArticle,name="addarticle"),
    path('article/<slug:slug>/', views.detail, name="detail"),
    path('update/<slug:slug>/', views.updateArticle, name="update"),
    path('delete/<slug:slug>/', views.deleteArticle, name="delete"),
    path("",views.articles,name="articles"),
    path("comment/<int:id>",views.addComment,name="comment"),
    path('makale/<int:id>/', views.detail, name='article_detail'),
    path("like/<int:id>/", views.like_article, name="like_article"),
    path('comment/like/<int:id>/', views.likeComment, name="like_comment"),
    path('comment/delete/<int:id>/', views.deleteComment, name="delete_comment"),
    ]
