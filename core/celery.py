"""Configurações do Celery para o projeto Orchestra."""

import os

from celery import Celery
from celery.app.task import Task

# Define o módulo de configurações padrão do Django para o programa 'celery'.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("orchestra")
app.config_from_object("django.conf:settings", namespace="CELERY")  # type: ignore[reportUnknownMemberType]

# Carrega módulos de tarefas de todas as apps Django registradas.
app.autodiscover_tasks()  # type: ignore[reportUnknownMemberType]


@app.task(bind=True, ignore_result=True)  # type: ignore[reportUnknownMemberType]
def debug_task(self: Task) -> None:  # type: ignore[reportUnknownParameterType, reportMissingTypeArgument] # Celery Task typing workaround
    """Tarefa de depuração que imprime a requisição da tarefa.

    Args:
        self: A instância da tarefa Celery.
    """
    print(f"Request: {self.request!r}")
    """Tarefa de depuração que imprime a requisição da tarefa.

    Args:
        self: A instância da tarefa Celery.
    """
    print(f"Request: {self.request!r}")
