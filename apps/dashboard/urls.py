from django.urls import path
from . import views

urlpatterns = [
    path('orchestra/', views.orchestra_view, name='orchestra'),
]
