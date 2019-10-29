from django.urls import path
from . import views

urlpatterns = [
    path('',views.LoginView.as_view(),name='login'),
    path('authorize',views.AuthorizeView.as_view(),name='authorize')
]
