import logging
import os
import subprocess

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CertificadoVeiculo

logger = logging.getLogger(__name__)


def run_automation_command(instance_id):
    """Executa o comando de automação em um processo separado e robusto.

    Redireciona a saída para arquivos de log específicos.
    """
    logger.info(
        f"[SIGNAL] run_automation_command INICIADO para Certificado ID: {instance_id}"
    )
    try:
        logger.info(
            f"[SIGNAL] run_automation_command chamado para Certificado ID: {instance_id}"
        )
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        python_executable = os.path.join(project_root, ".venv", "bin", "python")
        manage_py_path = os.path.join(project_root, "manage.py")

        command = [
            python_executable,
            manage_py_path,
            "automacao_documentos_ipiranga",
            str(instance_id),
        ]

        logger.info(f"[SIGNAL] Comando a ser executado: {' '.join(command)}")

        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
            project_root, ".playwright-browsers"
        )
        env["PATH"] = (
            os.path.join(project_root, ".venv", "bin")
            + os.pathsep
            + env.get("PATH", "")
        )
        logger.info(
            f"[SIGNAL] Variáveis de ambiente para o subprocesso: PLAYWRIGHT_BROWSERS_PATH={env['PLAYWRIGHT_BROWSERS_PATH']}, PATH={env['PATH']}"
        )

        logger.debug(
            f"[SIGNAL] Preparando para executar subprocess.Popen com o comando: {command}"
        )
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,  # Captura a saída padrão
            stderr=subprocess.PIPE,  # Captura a saída de erro
            preexec_fn=os.setsid,  # Desanexa o processo em sistemas Unix-like
            cwd=project_root,
            env=env,
        )
        stdout, stderr = process.communicate()
        logger.info(
            f"[SIGNAL] Subprocesso iniciado para Certificado ID: {instance_id}. PID: {process.pid}"
        )
        logger.info(f"[SIGNAL] STDOUT do subprocesso: {stdout.decode()}")
        logger.error(f"[SIGNAL] STDERR do subprocesso: {stderr.decode()}")

    except Exception as e:
        logger.error(
            f"[SIGNAL] Erro CRÍTICO ao iniciar o subprocesso para o Certificado ID {instance_id}: {e}",
            exc_info=True,
        )


@receiver(post_save, sender=CertificadoVeiculo)
def trigger_automacao_certificado(sender, instance, created, **kwargs):
    """Dispara a automação quando um novo CertificadoVeiculo pendente é criado."""
    logger.debug(
        f"[SIGNAL] trigger_automacao_certificado - Início. Sender: {sender.__name__}, Instance ID: {instance.id}, Created: {created}, Status: {instance.status}"
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
