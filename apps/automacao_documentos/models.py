from typing import TYPE_CHECKING, ClassVar

from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class Portal(models.Model):
    """Modelo para registrar os portais externos com os quais o sistema interage."""

    nome = models.CharField(max_length=255, unique=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    url_base = models.URLField(max_length=2000)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    # Adicionar campos para credenciais ou configurações específicas do portal, se necessário

    objects: "Manager[Portal]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Portal."""

        verbose_name = "Portal"
        verbose_name_plural = "Portais"

    def __str__(self) -> str:
        return self.nome


class Documento(models.Model):
    """Modelo para armazenar dados de documentos."""

    id = models.AutoField(primary_key=True) # Explicitly define ID
    TIPO_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("licenca", "Licença"),
        ("alvara", "Alvará"),
        ("certificado", "Certificado"),
        ("outros", "Outros"),
    ]

    portal = models.ForeignKey(
        Portal, on_delete=models.CASCADE, related_name="documentos"
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    numero = models.CharField(max_length=255, unique=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    status = models.CharField(max_length=50, default="ativo")  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_emissao = models.DateField(null=True, blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_validade = models.DateField(null=True, blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    arquivo_pdf = models.FileField(
        upload_to="documentos_automatizados/", null=True, blank=True
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    dados_extraidos = models.JSONField(
        null=True,
        blank=True,
        help_text="Dados extraídos do documento em formato JSON.",
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_criacao = models.DateTimeField(auto_now_add=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_atualizacao = models.DateTimeField(auto_now=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]

    objects: "Manager[Documento]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Documento."""

        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        unique_together = ("portal", "tipo", "numero")

    def __str__(self) -> str:
        return f"{self.tipo} - {self.numero} ({self.portal.nome})"


class Automacao(models.Model):
    """Modelo para agendar e registrar a execução de rotinas automáticas."""

    nome = models.CharField(max_length=255, unique=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    descricao = models.TextField(blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    comando_django = models.CharField(
        max_length=255,
        help_text="Nome do comando Django customizado a ser executado (ex: 'automacao_documentos_ipiranga').",
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    ativa = models.BooleanField(default=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    ultima_execucao = models.DateTimeField(null=True, blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    proxima_execucao = models.DateTimeField(null=True, blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    intervalo_execucao_minutos = models.IntegerField(
        default=60, help_text="Intervalo em minutos entre as execuções."
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]

    objects: "Manager[Automacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for Automacao."""

        verbose_name = "Automação"
        verbose_name_plural = "Automações"

    def __str__(self) -> str:
        return self.nome


class LogExecucaoAutomacao(models.Model):
    """Modelo para armazenar os logs detalhados de cada execução de Automação."""

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("sucesso", "Sucesso"),
        ("falha", "Falha"),
        ("parcial", "Sucesso Parcial"),
        ("alerta", "Alerta"),
    ]

    automacao = models.ForeignKey(
        Automacao, on_delete=models.CASCADE, related_name="logs"
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_inicio = models.DateTimeField(auto_now_add=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    data_fim = models.DateTimeField(null=True, blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    mensagem = models.TextField(blank=True)  # type: ignore[reportMissingTypeArgument, reportCallIssue]
    detalhes_json = models.JSONField(
        null=True, blank=True, help_text="Detalhes adicionais da execução em JSON."
    )  # type: ignore[reportMissingTypeArgument, reportCallIssue]

    objects: "Manager[LogExecucaoAutomacao]" = models.Manager()  # type: ignore[reportIncompatibleVariableOverride]

    class Meta:
        """Meta options for LogExecucaoAutomacao."""

        verbose_name = "Log de Execução de Automação"
        verbose_name_plural = "Logs de Execução de Automações"
        ordering: ClassVar[list[str]] = ["-data_inicio"]

    def __str__(self) -> str:
        return f"Log {self.id} - {self.automacao.nome} ({self.status})"  # type: ignore[reportAttributeAccessIssue]
