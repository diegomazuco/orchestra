from django.urls import path

from . import views

app_name = "analise_infracoes"

urlpatterns = [
    path("", views.listar_infracoes, name="listar_infracoes"),
]
