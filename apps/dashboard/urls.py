"""Definições de URL para o aplicativo dashboard."""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.orchestra_view, name="orchestra"),
    path("process-documents/", views.process_documents_view, name="process_documents"),
    path(
        "check-certificate-status/<int:certificate_id>/",
        views.check_certificate_status_view,
        name="check_certificate_status",
    ),
]
