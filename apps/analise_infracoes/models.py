"""Modelos para o aplicativo analise_infracoes."""

from typing import TYPE_CHECKING, ClassVar

from django.db import models
from django.db.models import (
    CharField,
    DateTimeField,
    DecimalField,
    IntegerField,
    JSONField,
)  # Import specific field types for better typing

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class Infracao(models.Model):
    """Representa uma infração de trânsito analisada."""

    placa_veiculo: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=10, help_text="Placa do veículo que cometeu a infração."
    )
    data_hora: DateTimeField = models.DateTimeField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        help_text="Data e hora em que a infração ocorreu."
    )
    local: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=255, help_text="Local da infração."
    )
    tipo_infracao: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=255, help_text="Descrição do tipo de infração."
    )
    valor: DecimalField = models.DecimalField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_digits=10, decimal_places=2, help_text="Valor da multa."
    )
    pontos_carteira: IntegerField = models.IntegerField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        help_text="Número de pontos atribuídos à carteira."
    )
    status: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=50,
        default="nova",
        help_text="Status da infração (ex: nova, em análise, paga).",
    )
    dados_origem: JSONField = models.JSONField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        help_text="Dados brutos originais do banco de dados de origem."
    )

    objects: "Manager[Infracao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Metadados para o modelo Infracao."""

        verbose_name = "Infração"
        verbose_name_plural = "Infrações"
        ordering: ClassVar[list[str]] = ["-data_hora"]

    def __str__(self) -> str:
        """Retorna uma representação em string da infração."""
        return f"Infração {self.id} - {self.placa_veiculo} em {self.data_hora.strftime('%d/%m/%Y')}"  # type: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
