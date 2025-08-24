import logging
from typing import Any

from celery import shared_task  # type: ignore

from apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga import (
    Command as AutomacaoIpirangaCommand,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_automacao_ipiranga_task(self: Any, certificado_veiculo_id: int) -> None:
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
        command_instance.handle_task(certificado_veiculo_id)  # type: ignore
        logger.info(
            f"Tarefa Celery concluída para CertificadoVeiculo ID: {certificado_veiculo_id}"
        )
    except Exception as e:
        logger.error(
            f"Erro na tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}: {e}",
            exc_info=True,
        )
