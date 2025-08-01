from django.urls import path

from . import views

app_name = "automacao_ipiranga"

urlpatterns = [
    path("iniciar_automacao/", views.iniciar_automacao, name="iniciar_automacao"),
]
