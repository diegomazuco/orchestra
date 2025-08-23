from celery import shared_task
import logging
from apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga import Command as AutomacaoIpirangaCommand

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_automacao_ipiranga_task(self, certificado_veiculo_id):
    logger.info(f"Iniciando tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}")
    try:
        # Instancia o comando e executa a lógica principal
        command_instance = AutomacaoIpirangaCommand()
        command_instance.handle_task(certificado_veiculo_id)
        logger.info(f"Tarefa Celery concluída para CertificadoVeiculo ID: {certificado_veiculo_id}")
    except Exception as e:
        logger.error(f"Erro na tarefa Celery para CertificadoVeiculo ID: {certificado_veiculo_id}: {e}", exc_info=True)
        # Opcional: re-tentar a tarefa em caso de falha
        # raise self.retry(exc=e, countdown=60, max_retries=3)