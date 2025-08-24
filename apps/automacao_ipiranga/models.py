"""Modelos para o aplicativo automacao_ipiranga."""

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from django.db import models
from django.db.models import (
    AutoField,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    IntegerField,
)  # Import specific field types for better typing

from apps.common.storage import OriginalFilenameStorage

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class VeiculoIpiranga(models.Model):
    """Modelo para armazenar informações de veículos Ipiranga."""

    id: AutoField[int, int] = models.AutoField(primary_key=True)
    placa: CharField[str, str] = models.CharField(max_length=10, unique=True)
    status_documentos: CharField[str, str] = models.CharField(
        max_length=255, blank=True, default=""
    )
    data_atualizacao: DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True
    )

    objects: ClassVar[Manager["VeiculoIpiranga"]] = models.Manager()  # type: ignore[reportIncompatibleVariableOverride, reportUndefinedVariable]

    class Meta:
        """Meta options para o modelo VeiculoIpiranga."""

        app_label = "automacao_ipiranga"

    def __str__(self) -> str:
        """Retorna a placa do veículo."""
        return str(self.placa)  # type: ignore[reportUnknownMemberType, reportAttributeAccessIssue]


class CertificadoVeiculo(models.Model):
    """Modelo para armazenar informações de certificados de veículos."""

    id: AutoField[int, int] = models.AutoField(primary_key=True)
    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pendente", "Pendente de Envio"),
        ("enviado", "Enviado com Sucesso"),
        ("falha", "Falha no Envio"),
        ("falha_max_tentativas", "Falha: Máximo de Tentativas Atingido"),
        ("falha_outros_vencidos", "Falha: Outros Certificados Vencidos"),
    ]

    veiculo: ForeignKey["VeiculoIpiranga", "VeiculoIpiranga"] = models.ForeignKey(
        VeiculoIpiranga, on_delete=models.CASCADE, related_name="certificados"
    )
    nome: CharField[str, str] = models.CharField(max_length=255)
    arquivo: FileField = models.FileField(
        upload_to="certificados_veiculos/", storage=OriginalFilenameStorage()
    )
    status: CharField[str, str] = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="pendente"
    )
    tentativas_automacao: IntegerField[int, int] = models.IntegerField(default=0)
    data_criacao: DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )
    data_atualizacao: DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True
    )
    error_message: CharField[str, str] = models.CharField(
        max_length=500, blank=True, default=""
    )

    objects: ClassVar[Manager["CertificadoVeiculo"]] = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    def __str__(self) -> str:
        """Retorna o nome do certificado e a placa do veículo associado."""
        return f"{self.nome} - {self.veiculo.placa}"
