"""Sinais Django para o aplicativo automacao_ipiranga."""

import logging
from typing import Any, cast

from django.db import transaction
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.automacao_ipiranga.models import CertificadoVeiculo
from apps.automacao_ipiranga.tasks import run_automacao_ipiranga_task

logger = logging.getLogger(__name__)


@receiver(
    post_save, sender="automacao_ipiranga.CertificadoVeiculo"
)  # Use string reference
def trigger_automacao_certificado(
    sender: type[Model], instance: Model, created: bool, **kwargs: dict[str, Any]
) -> None:
    """Dispara a automação quando um novo CertificadoVeiculo pendente é criado."""
    # A verificação do modelo pode ser feita diretamente no if abaixo
    # usando o sender ou o próprio instance, tornando a busca dinâmica desnecessária.

    certificado_instance = cast(CertificadoVeiculo, instance)

    logger.debug(
        f"[SIGNAL] trigger_automacao_certificado - Início. "
        f"Sender: {sender.__name__}, Instance ID: {certificado_instance.id}, "  # type: ignore[reportUnknownMemberType]
        f"Created: {created}, Status: {certificado_instance.status}"  # type: ignore[reportUnknownMemberType]
    )
    if created and certificado_instance.status == "pendente":  # type: ignore[reportUnknownMemberType]
        logger.info(
            f"[SIGNAL] Condições atendidas (objeto criado e pendente). Disparando automação para o Certificado ID: {certificado_instance.id} via Celery."  # type: ignore[reportUnknownMemberType]
        )
        transaction.on_commit(
            lambda: run_automacao_ipiranga_task.delay(certificado_instance.id)  # type: ignore[reportUnknownMemberType]
        )
    else:
        logger.info(
            f"[SIGNAL] Condições não atendidas (objeto não criado ou status não pendente). Nenhuma automação foi disparada para o Certificado ID: {certificado_instance.id}."  # type: ignore[reportUnknownMemberType]
        )
