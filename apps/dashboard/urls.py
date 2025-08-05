from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.orchestra_view, name="orchestra"),
    path("process-documents/", views.process_documents_view, name="process_documents"),
]
