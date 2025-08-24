import os
from typing import Any

from celery import Celery  # type: ignore

# Define o módulo de configurações padrão do Django para o programa 'celery'.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("orchestra")

# Usando uma string aqui significa que o worker não precisa serializar
# o objeto de configuração para processos filhos.
# - namespace='CELERY' significa que todas as chaves de configuração relacionadas ao Celery
# devem ter o prefixo `CELERY_` (ex: CELERY_BROKER_URL).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Carrega módulos de tarefas de todas as apps Django registradas.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)  # type: ignore
def debug_task(self: Any) -> None:
    """Tarefa de depuração que imprime a requisição da tarefa.

    Args:
        self: A instância da tarefa Celery.
    """
    print(f"Request: {self.request!r}")
