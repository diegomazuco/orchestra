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

    id: AutoField = models.AutoField(primary_key=True)  # type: ignore
    placa: CharField = models.CharField(max_length=10, unique=True)  # type: ignore
    status_documentos: CharField = models.CharField(  # type: ignore
        max_length=255, blank=True, default=""
    )
    data_atualizacao: DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore

    objects: "Manager[VeiculoIpiranga]"  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options para o modelo VeiculoIpiranga."""

        app_label = "automacao_ipiranga"

    def __str__(self) -> str:
        return str(self.placa)  # type: ignore


class CertificadoVeiculo(models.Model):
    """Modelo para armazenar informações de certificados de veículos."""

    id: AutoField = models.AutoField(primary_key=True)  # type: ignore
    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pendente", "Pendente de Envio"),
        ("enviado", "Enviado com Sucesso"),
        ("falha", "Falha no Envio"),
        ("falha_max_tentativas", "Falha: Máximo de Tentativas Atingido"),
        ("falha_outros_vencidos", "Falha: Outros Certificados Vencidos"),
    ]

    veiculo: ForeignKey = models.ForeignKey(  # type: ignore
        VeiculoIpiranga, on_delete=models.CASCADE, related_name="certificados"
    )
    nome: CharField = models.CharField(max_length=255)  # type: ignore
    arquivo: FileField = models.FileField(  # type: ignore
        upload_to="certificados_veiculos/", storage=OriginalFilenameStorage()
    )
    status: CharField = models.CharField(  # type: ignore
        max_length=30, choices=STATUS_CHOICES, default="pendente"
    )
    tentativas_automacao: IntegerField = models.IntegerField(default=0)  # type: ignore
    data_criacao: DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore
    data_atualizacao: DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore
    error_message: CharField = models.CharField(max_length=500, blank=True, default="")  # type: ignore

    objects: "Manager[CertificadoVeiculo]"  # type: ignore[reportIncompatibleVariableOverride]

    def __str__(self) -> str:
        return f"{self.nome} - {self.veiculo.placa}"  # type: ignore
