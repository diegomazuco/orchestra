from django.contrib import admin

from .models import Infracao


@admin.register(Infracao)
class InfracaoAdmin(admin.ModelAdmin):
    """Define a interface de administração para o modelo Infracao."""

    list_display = (
        "placa_veiculo",
        "data_hora",
        "local",
        "tipo_infracao",
        "valor",
        "status",
    )
    list_filter = ("status", "tipo_infracao", "data_hora")
    search_fields = ("placa_veiculo", "local")
    readonly_fields = ("dados_origem",)
