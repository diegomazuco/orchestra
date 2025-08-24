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

    nome: CharField = models.CharField(max_length=255, unique=True)  # type: ignore
    url_base: URLField = models.URLField(max_length=2000)  # type: ignore
    # Adicionar campos para credenciais ou configurações específicas do portal, se necessário

    objects: "Manager[Portal]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Portal."""

        verbose_name = "Portal"
        verbose_name_plural = "Portais"

    def __str__(self) -> str:
        return self.nome  # type: ignore


class Documento(models.Model):
    """Modelo para armazenar dados de documentos."""

    id: AutoField = models.AutoField(primary_key=True)  # type: ignore
    TIPO_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("licenca", "Licença"),
        ("alvara", "Alvará"),
        ("certificado", "Certificado"),
        ("outros", "Outros"),
    ]

    portal: ForeignKey = models.ForeignKey(  # type: ignore
        Portal, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo: CharField = models.CharField(max_length=50, choices=TIPO_CHOICES)  # type: ignore
    numero: CharField = models.CharField(max_length=255, unique=True)  # type: ignore
    status: CharField = models.CharField(max_length=50, default="ativo")  # type: ignore
    data_emissao: DateField = models.DateField(null=True, blank=True)  # type: ignore
    data_validade: DateField = models.DateField(null=True, blank=True)  # type: ignore
    arquivo_pdf: FileField = models.FileField(  # type: ignore
        upload_to="documentos_automatizados/", null=True, blank=True
    )
    dados_extraidos: JSONField = models.JSONField(  # type: ignore
        null=True,
        blank=True,
        help_text="Dados extraídos do documento em formato JSON.",
    )
    data_criacao: DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore
    data_atualizacao: DateTimeField = models.DateTimeField(auto_now=True)  # type: ignore

    objects: "Manager[Documento]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Documento."""

        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        unique_together = ("portal", "tipo", "numero")

    def __str__(self) -> str:
        return f"{self.tipo} - {self.numero} ({self.portal.nome})"  # type: ignore


class Automacao(models.Model):
    """Modelo para agendar e registrar a execução de rotinas automáticas."""

    nome: CharField = models.CharField(max_length=255, unique=True)  # type: ignore
    descricao: TextField = models.TextField(blank=True)  # type: ignore
    comando_django: CharField = models.CharField(  # type: ignore
        max_length=255,
        help_text="Nome do comando Django customizado a ser executado (ex: 'automacao_documentos_ipiranga').",
    )
    ativa: BooleanField = models.BooleanField(default=True)  # type: ignore
    ultima_execucao: DateTimeField = models.DateTimeField(null=True, blank=True)  # type: ignore
    proxima_execucao: DateTimeField = models.DateTimeField(null=True, blank=True)  # type: ignore
    intervalo_execucao_minutos: IntegerField = models.IntegerField(  # type: ignore
        default=60, help_text="Intervalo em minutos entre as execuções."
    )

    objects: "Manager[Automacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Automacao."""

        verbose_name = "Automação"
        verbose_name_plural = "Automações"

    def __str__(self) -> str:
        return self.nome  # type: ignore


class LogExecucaoAutomacao(models.Model):
    """Modelo para armazenar os logs detalhados de cada execução de Automação."""

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("sucesso", "Sucesso"),
        ("falha", "Falha"),
        ("parcial", "Sucesso Parcial"),
        ("alerta", "Alerta"),
    ]

    automacao: ForeignKey = models.ForeignKey(  # type: ignore
        Automacao, on_delete=models.CASCADE, related_name="logs"
    )
    data_inicio: DateTimeField = models.DateTimeField(auto_now_add=True)  # type: ignore
    data_fim: DateTimeField = models.DateTimeField(null=True, blank=True)  # type: ignore
    status: CharField = models.CharField(max_length=50, choices=STATUS_CHOICES)  # type: ignore
    mensagem: TextField = models.TextField(blank=True)  # type: ignore
    detalhes_json: JSONField = models.JSONField(  # type: ignore
        null=True, blank=True, help_text="Detalhes adicionais da execução em JSON."
    )

    objects: "Manager[LogExecucaoAutomacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for LogExecucaoAutomacao."""

        verbose_name = "Log de Execução de Automação"
        verbose_name_plural = "Logs de Execução de Automações"
        ordering: ClassVar[list[str]] = ["-data_inicio"]

    def __str__(self) -> str:
        return f"Log {int(self.id)} - {self.automacao.nome} ({self.status})"  # type: ignore[reportUnknownMemberType]
