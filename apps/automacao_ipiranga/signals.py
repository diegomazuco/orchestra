import logging
import os
import subprocess
import sys

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CertificadoVeiculo

logger = logging.getLogger(__name__)


def run_automation_command(instance_id):
    """Executa o comando de automação em um processo separado e robusto.

    Redireciona a saída para arquivos de log específicos.
    """
    try:
        python_executable = sys.executable
        manage_py_path = os.path.abspath("./manage.py")
        project_root = os.path.dirname(manage_py_path)

        command = [
            python_executable,
            manage_py_path,
            "automacao_documentos_ipiranga",
            str(instance_id),
        ]

        logger.info(f"[SIGNAL] Executando comando em subprocesso: {' '.join(command)}")

        # Inicia o processo em segundo plano, desanexando-o completamente
        # Redireciona stdout e stderr para /dev/null para evitar que o processo pai espere
        # e para que o logging seja tratado pelo sistema de logging do Django no subprocesso.
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,  # Essencial para desanexar em Unix-like systems
            cwd=project_root,
        )
        logger.info(
            f"[SIGNAL] Subprocesso iniciado para Certificado ID: {instance_id}. PID: {process.pid}"
        )

    except Exception as e:
        logger.error(
            f"[SIGNAL] Erro CRÍTICO ao iniciar o subprocesso para o Certificado ID {instance_id}: {e}",
            exc_info=True,
        )


@receiver(post_save, sender=CertificadoVeiculo)
def trigger_automacao_certificado(sender, instance, created, **kwargs):
    """Dispara a automação quando um novo CertificadoVeiculo pendente é criado."""
    logger.info(
        f"[SIGNAL] Sinal post_save recebido para CertificadoVeiculo ID: {instance.id} (Created: {created}, Status: {instance.status})"
    )
    if created and instance.status == "pendente":
        logger.info(
            f"[SIGNAL] Condições atendidas. Disparando automação para o Certificado ID: {instance.id}"
        )
        run_automation_command(instance.id)
    else:
        logger.info(
            f"[SIGNAL] Condições não atendidas. Nenhuma automação foi disparada para o Certificado ID: {instance.id}."
        )
