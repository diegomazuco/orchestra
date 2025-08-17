import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from django.db import transaction
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def run_automation_command(instance_id: int) -> None:
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

        display = os.environ.get("DISPLAY")
        if display:
            env["DISPLAY"] = display
            logger.info(f"[SIGNAL] Usando DISPLAY: {display}")
        else:
            logger.warning(
                "[SIGNAL] A variável de ambiente DISPLAY não está definida. A automação pode falhar ao tentar abrir uma interface gráfica."
            )

        logger.info(
            f"[SIGNAL] Iniciando subprocesso com Popen para o Certificado ID: {instance_id}"
        )
        logger.info(
            "[SIGNAL] Redirecionando STDOUT e STDERR do subprocesso para logs/django.log"
        )
        with open(project_root / "logs" / "django.log", "a") as log_file:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=log_file,
                text=True,
                cwd=str(project_root),
                env=env,
            )
            logger.info(
                f"[SIGNAL] Subprocesso com Popen iniciado para Certificado ID: {process.pid}"
            )

        logger.info(
            f"[SIGNAL] Subprocesso para o Certificado ID: {instance_id} iniciado. Logs serão gravados em logs/django.log."
        )

    except Exception as e:
        logger.critical(
            f"[SIGNAL] Erro CRÍTICO ao iniciar o subprocesso para o Certificado ID {instance_id}: {e}",
            exc_info=True,
        )


@receiver(
    post_save, sender="automacao_ipiranga.CertificadoVeiculo"
)  # Use string reference
def trigger_automacao_certificado(
    sender: type[Model], instance: Model, created: bool, **kwargs: Any
) -> None:
    """Dispara a automação quando um novo CertificadoVeiculo pendente é criado."""
    # A verificação do modelo pode ser feita diretamente no if abaixo
    # usando o sender ou o próprio instance, tornando a busca dinâmica desnecessária.

    logger.debug(
        f"[SIGNAL] trigger_automacao_certificado - Início. "
        f"Sender: {sender.__name__}, Instance ID: {instance.id}, "  # type: ignore
        f"Created: {created}, Status: {instance.status}"  # type: ignore
    )
    if instance.status == "pendente":  # type: ignore
        logger.info(
            f"[SIGNAL] Condições atendidas. Disparando automação para o Certificado ID: {instance.id}"  # type: ignore
        )
        transaction.on_commit(lambda: run_automation_command(instance.id))  # type: ignore
    else:
        logger.info(
            f"[SIGNAL] Condições não atendidas. Nenhuma automação foi disparada para o Certificado ID: {instance.id}."  # type: ignore
        )
