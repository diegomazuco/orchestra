from typing import ClassVar

from django.db import models


class Infracao(models.Model):
    """Representa uma infração de trânsito analisada."""

    placa_veiculo = models.CharField(
        max_length=10, help_text="Placa do veículo que cometeu a infração."
    )
    data_hora = models.DateTimeField(help_text="Data e hora em que a infração ocorreu.")
    local = models.CharField(max_length=255, help_text="Local da infração.")
    tipo_infracao = models.CharField(
        max_length=255, help_text="Descrição do tipo de infração."
    )
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor da multa."
    )
    pontos_carteira = models.IntegerField(
        help_text="Número de pontos atribuídos à carteira."
    )
    status = models.CharField(
        max_length=50,
        default="nova",
        help_text="Status da infração (ex: nova, em análise, paga).",
    )
    dados_origem = models.JSONField(
        help_text="Dados brutos originais do banco de dados de origem."
    )

    class Meta:
        """Metadados para o modelo Infracao."""

        verbose_name = "Infração"
        verbose_name_plural = "Infrações"
        ordering: ClassVar[list[str]] = ["-data_hora"]

    def __str__(self):
        return f"Infração {self.id} - {self.placa_veiculo} em {self.data_hora.strftime('%d/%m/%Y')}"
