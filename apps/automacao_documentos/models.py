"""Modelos para o aplicativo automacao_documentos."""

from typing import TYPE_CHECKING, ClassVar

from django.db import models
from django.db.models import (
    AutoField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    FileField,
    ForeignKey,
    IntegerField,
    JSONField,
    TextField,
    URLField,
)  # Import specific field types for better typing

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class Portal(models.Model):
    """Modelo para registrar os portais externos com os quais o sistema interage."""

    nome: CharField = models.CharField(max_length=255, unique=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    url_base: URLField = models.URLField(max_length=2000)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    # Adicionar campos para credenciais ou configurações específicas do portal, se necessário

    objects: "Manager[Portal]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Portal."""

        verbose_name = "Portal"
        verbose_name_plural = "Portais"

    def __str__(self) -> str:
        """Retorna o nome do portal."""
        return self.nome  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]


class Documento(models.Model):
    """Modelo para armazenar dados de documentos."""

    id: AutoField = models.AutoField(primary_key=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    TIPO_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("licenca", "Licença"),
        ("alvara", "Alvará"),
        ("certificado", "Certificado"),
        ("outros", "Outros"),
    ]

    portal: ForeignKey = models.ForeignKey(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        Portal, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo: CharField = models.CharField(max_length=50, choices=TIPO_CHOICES)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    numero: CharField = models.CharField(max_length=255, unique=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    status: CharField = models.CharField(max_length=50, default="ativo")  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_emissao: DateField = models.DateField(null=True, blank=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_validade: DateField = models.DateField(null=True, blank=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    arquivo_pdf: FileField = models.FileField(
        upload_to="documentos_automatizados/", null=True, blank=True
    )
    dados_extraidos: JSONField = models.JSONField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        null=True,
        blank=True,
        help_text="Dados extraídos do documento em formato JSON.",
    )
    data_criacao: DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_atualizacao: DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]

    objects: "Manager[Documento]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Documento."""

        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        unique_together = ("portal", "tipo", "numero")

    def __str__(self) -> str:
        """Retorna uma representação em string do documento."""
        return f"{self.tipo} - {self.numero} ({self.portal.nome})"  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]


class Automacao(models.Model):
    """Modelo para agendar e registrar a execução de rotinas automáticas."""

    nome: CharField = models.CharField(max_length=255, unique=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    descricao: TextField = models.TextField(blank=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    comando_django: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=255,
        help_text="Nome do comando Django customizado a ser executado (ex: 'automacao_documentos_ipiranga').",
    )
    ativa: BooleanField = models.BooleanField(default=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    ultima_execucao: DateTimeField = models.DateTimeField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        null=True, blank=True
    )
    proxima_execucao: DateTimeField = models.DateTimeField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        null=True, blank=True
    )
    intervalo_execucao_minutos: IntegerField = models.IntegerField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        default=60, help_text="Intervalo em minutos entre as execuções."
    )

    objects: "Manager[Automacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Automacao."""

        verbose_name = "Automação"
        verbose_name_plural = "Automações"

    def __str__(self) -> str:
        """Retorna o nome da automação."""
        return self.nome  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]


class LogExecucaoAutomacao(models.Model):
    """Modelo para armazenar os logs detalhados de cada execução de Automação."""

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("sucesso", "Sucesso"),
        ("falha", "Falha"),
        ("parcial", "Sucesso Parcial"),
        ("alerta", "Alerta"),
    ]

    automacao: ForeignKey = models.ForeignKey(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        Automacao, on_delete=models.CASCADE, related_name="logs"
    )
    data_inicio: DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    data_fim: DateTimeField = models.DateTimeField(null=True, blank=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    status: CharField = models.CharField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        max_length=50, choices=STATUS_CHOICES
    )
    mensagem: TextField = models.TextField(blank=True)  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
    detalhes_json: JSONField = models.JSONField(  # type: ignore[reportUnknownVariableType, reportMissingTypeArgument]
        null=True,
        blank=True,
        help_text="Detalhes adicionais da execução em JSON.",
    )

    objects: "Manager[LogExecucaoAutomacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for LogExecucaoAutomacao."""

        verbose_name = "Log de Execução de Automação"
        verbose_name_plural = "Logs de Execução de Automações"
        ordering: ClassVar[list[str]] = ["-data_inicio"]

    def __str__(self) -> str:
        """Retorna uma representação em string do log de execução."""
        return f"Log {int(self.id)} - {self.automacao.nome} ({self.status})"  # type: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
