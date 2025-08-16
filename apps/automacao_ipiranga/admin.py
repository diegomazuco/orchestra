from django.contrib import admin

from .models import CertificadoVeiculo, VeiculoIpiranga


@admin.register(VeiculoIpiranga)
class VeiculoIpirangaAdmin(admin.ModelAdmin[VeiculoIpiranga]):
    """Administração de Veículos Ipiranga."""

    list_display = ("placa", "status_documentos", "data_atualizacao")
    search_fields = ("placa",)


@admin.register(CertificadoVeiculo)
class CertificadoVeiculoAdmin(admin.ModelAdmin[CertificadoVeiculo]):
    """Administração de Certificados de Veículos."""

    list_display = ("nome", "veiculo", "status", "data_atualizacao")
    search_fields = ("nome", "veiculo__placa")
    list_filter = ("status", "data_criacao")
