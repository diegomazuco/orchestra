from django.contrib import admin

from .models import CertificadoVeiculo, VeiculoIpiranga


@admin.register(VeiculoIpiranga)
class VeiculoIpirangaAdmin(admin.ModelAdmin):
    list_display = ('placa', 'renavam', 'status_documentos', 'data_atualizacao')
    search_fields = ('placa', 'renavam')

@admin.register(CertificadoVeiculo)
class CertificadoVeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'veiculo', 'status', 'data_atualizacao')
    search_fields = ('nome', 'veiculo__placa')
    list_filter = ('status', 'data_criacao')
