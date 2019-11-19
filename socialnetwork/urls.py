from django.urls import path
from . import views

urlpatterns = [
    path('',views.RegisterView.as_view(),name='register'),
    path('login/<str:_id>/<str:username>',views.LoginView.as_view(),name='login'),
    path('authorize',views.AuthorizeView.as_view(),name='authorize'),
    path('signin',views.SignInFireBaseView.as_view(),name='signin'),
    path('dashboard/<str:_id>',views.DashboardView.as_view(),name='dashboard'),
    path('feed/<str:_id>',views.FeedView.as_view(),name='feed'),
    path('users/<str:_id>',views.usersView,name='users'),
    path('share/<str:_id>',views.ShareView,name='share')
]
