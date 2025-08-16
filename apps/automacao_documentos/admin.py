from django.contrib import admin

from .models import Automacao, Documento, LogExecucaoAutomacao, Portal


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin[Portal]):
    """Administração de Portais."""

    list_display = ("nome", "url_base")
    search_fields = ("nome", "url_base")


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin[Documento]):
    """Administração de Documentos."""

    list_display = (
        "numero",
        "tipo",
        "portal",
        "status",
        "data_validade",
        "data_atualizacao",
    )
    list_filter = ("tipo", "portal", "status")
    search_fields = ("numero", "portal__nome")
    raw_id_fields = ("portal",)


@admin.register(Automacao)
class AutomacaoAdmin(admin.ModelAdmin[Automacao]):
    """Administração de Automações."""

    list_display = (
        "nome",
        "comando_django",
        "ativa",
        "ultima_execucao",
        "proxima_execucao",
    )
    list_filter = ("ativa",)
    search_fields = ("nome", "comando_django")


@admin.register(LogExecucaoAutomacao)
class LogExecucaoAutomacaoAdmin(admin.ModelAdmin[LogExecucaoAutomacao]):
    """Administração de Logs de Execução de Automação."""

    list_display = (
        "automacao",
        "data_inicio",
        "status",
        "mensagem",
    )
    list_filter = ("automacao", "status")
    search_fields = ("automacao__nome", "mensagem")
    readonly_fields = (
        "automacao",
        "data_inicio",
        "data_fim",
        "status",
        "mensagem",
        "detalhes_json",
    )
