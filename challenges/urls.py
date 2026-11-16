from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenge_list, name='challenge_list'),
    path('<int:pk>/', views.challenge_detail, name='challenge_detail'),
    path('<int:pk>/submit/', views.challenge_submit, name='challenge_submit'),
    path('create/', views.challenge_create, name='challenge_create'),
    path('<int:pk>/edit/', views.challenge_edit, name='challenge_edit'),
    path('<int:pk>/delete/', views.challenge_delete, name='challenge_delete'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
]
