from typing import TYPE_CHECKING, ClassVar

from django.db import models

from apps.common.storage import OriginalFilenameStorage

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class VeiculoIpiranga(models.Model):
    """Modelo para armazenar informações de veículos Ipiranga."""

    placa: models.CharField = models.CharField(max_length=10, unique=True)  # type: ignore[reportUnknownVariableType, reportUnknownArgumentType, reportMissingTypeArgument, reportCallIssue]
    status_documentos: models.CharField = models.CharField(
        max_length=255, blank=True, default=""
    )  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_atualizacao: models.DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore[reportUnknownVariableType]

    objects: "Manager[VeiculoIpiranga]"  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options para o modelo VeiculoIpiranga."""

        app_label = "automacao_ipiranga"

    def __str__(self) -> str:
        return str(self.placa)


class CertificadoVeiculo(models.Model):
    """Modelo para armazenar informações de certificados de veículos."""

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pendente", "Pendente de Envio"),
        ("enviado", "Enviado com Sucesso"),
        ("falha", "Falha no Envio"),
    ]

    veiculo: models.ForeignKey = models.ForeignKey(
        VeiculoIpiranga, on_delete=models.CASCADE, related_name="certificados"
    )  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    nome: models.CharField = models.CharField(max_length=255)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    arquivo: models.FileField = models.FileField(
        upload_to="certificados_veiculos/", storage=OriginalFilenameStorage()
    )  # type: ignore[reportUnknownVariableType]
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pendente"
    )  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_criacao: models.DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore[reportUnknownVariableType]
    data_atualizacao: models.DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore[reportUnknownVariableType]

    objects: "Manager[CertificadoVeiculo]"  # type: ignore[reportIncompatibleVariableOverride]

    def __str__(self) -> str:
        return f"{self.nome} - {self.veiculo.placa}"
