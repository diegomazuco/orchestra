"""Tarefas Celery para o aplicativo automacao_ipiranga."""

import asyncio
import logging

from celery import Celery
from celery.app.task import Task

from apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga import (
    Command as AutomacaoIpirangaCommand,
)

logger = logging.getLogger(__name__)

app = Celery("orchestra")
app.config_from_object("django.conf:settings", namespace="CELERY")  # type: ignore[reportUnknownMemberType]
app.autodiscover_tasks()  # type: ignore[reportUnknownMemberType]


@app.task(bind=True)  # type: ignore[reportUnknownMemberType]
def run_automacao_ipiranga_task(self: Task, certificado_veiculo_id: int) -> None:  # type: ignore[reportUnknownParameterType, reportMissingTypeArgument] # Celery Task typing workaround
    """Executa a tarefa de automação Ipiranga para um certificado de veículo específico.

    Args:
        self: A instância da tarefa Celery.
        certificado_veiculo_id: O ID do CertificadoVeiculo a ser processado.
    """
    logger.info(
        f"Iniciando tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}"
    )
    try:
        # Instancia o comando e executa a lógica principal
        command_instance = AutomacaoIpirangaCommand()
        asyncio.run(command_instance.handle_async(certificado_veiculo_id))
        logger.info(
            f"Tarefa Celery concluída para CertificadoVeiculo ID: {certificado_veiculo_id}"
        )
    except Exception as e:
        logger.error(
            f"Erro na tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}: {e}",
            exc_info=True,
        )

    """Executa a tarefa de automação Ipiranga para um certificado de veículo específico.

    Args:
        self: A instância da tarefa Celery.
        certificado_veiculo_id: O ID do CertificadoVeiculo a ser processado.
    """
    logger.info(
        f"Iniciando tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}"
    )
    try:
        # Instancia o comando e executa a lógica principal
        command_instance = AutomacaoIpirangaCommand()
        asyncio.run(command_instance.handle_async(certificado_veiculo_id))
        logger.info(
            f"Tarefa Celery concluída para CertificadoVeiculo ID: {certificado_veiculo_id}"
        )
    except Exception as e:
        logger.error(
            f"Erro na tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}: {e}",
            exc_info=True,
        )
