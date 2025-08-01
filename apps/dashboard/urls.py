from django.urls import path

from . import views

urlpatterns = [
    path("", views.orchestra_view, name="orchestra"),
    path("process-documents/", views.process_documents_view, name="process_documents"),
]
