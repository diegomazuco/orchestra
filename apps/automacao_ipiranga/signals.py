import logging
import os
import subprocess
import sys
from pathlib import Path

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CertificadoVeiculo

logger = logging.getLogger(__name__)


def run_automation_command(instance_id):
    """Executa o comando de automação em um processo separado e robusto."""
    logger.info(
        f"[SIGNAL] Iniciando run_automation_command para Certificado ID: {instance_id}"
    )
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        python_executable = project_root / ".venv" / "bin" / "python"
        manage_py_path = project_root / "manage.py"

        command = [
            str(python_executable),
            str(manage_py_path),
            "automacao_documentos_ipiranga",
            str(instance_id),
        ]

        logger.info(f"[SIGNAL] Comando a ser executado: {' '.join(command)}")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        # Add virtual environment's site-packages to PYTHONPATH
        site_packages_path = (
            project_root
            / ".venv"
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
        if site_packages_path.exists():
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{site_packages_path}:{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = str(site_packages_path)
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(project_root / ".playwright-browsers")

        logger.info(
            f"[SIGNAL] Iniciando subprocesso com Popen para o Certificado ID: {instance_id}"
        )
        process = subprocess.Popen(
            command,  # Use the original 'command' list
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
            env=env,
        )
        logger.info(
            f"[SIGNAL] Subprocesso com Popen iniciado para Certificado ID: {instance_id}. PID: {process.pid}"
        )

        stdout, stderr = process.communicate()

        logger.info(
            f"[SIGNAL] Subprocesso para o Certificado ID: {instance_id} concluído."
        )

        if stdout:
            logger.info(
                f"[SIGNAL] STDOUT do subprocesso (ID: {instance_id}):\n{stdout}"
            )
        if stderr:
            logger.error(
                f"[SIGNAL] STDERR do subprocesso (ID: {instance_id}):\n{stderr}"
            )

    except Exception as e:
        logger.critical(
            f"[SIGNAL] Erro CRÍTICO ao iniciar o subprocesso para o Certificado ID {instance_id}: {e}",
            exc_info=True,
        )


@receiver(post_save, sender=CertificadoVeiculo)
def trigger_automacao_certificado(sender, instance, created, **kwargs):
    """Dispara a automação quando um novo CertificadoVeiculo pendente é criado."""
    logger.debug(
        f"[SIGNAL] trigger_automacao_certificado - Início. "
        f"Sender: {sender.__name__}, Instance ID: {instance.id}, "
        f"Created: {created}, Status: {instance.status}"
    )
    if instance.status == "pendente":
        logger.info(
            f"[SIGNAL] Condições atendidas. Disparando automação para o Certificado ID: {instance.id}"
        )
        transaction.on_commit(lambda: run_automation_command(instance.id))
    else:
        logger.info(
            f"[SIGNAL] Condições não atendidas. Nenhuma automação foi disparada para o Certificado ID: {instance.id}."
        )
