from typing import ClassVar

from django.db import models

from apps.common.storage import OriginalFilenameStorage

# Instancia o storage personalizado
original_filename_storage = OriginalFilenameStorage()


class VeiculoIpiranga(models.Model):
    """Modelo para armazenar informações de veículos Ipiranga."""

    placa = models.CharField(max_length=10, unique=True)
    status_documentos = models.CharField(max_length=255, blank=True, default="")
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options para o modelo VeiculoIpiranga."""

        app_label = "automacao_ipiranga"

    def __str__(self):
        return str(self.placa)


class CertificadoVeiculo(models.Model):
    """Modelo para armazenar informações de certificados de veículos."""

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pendente", "Pendente de Envio"),
        ("enviado", "Enviado com Sucesso"),
        ("falha", "Falha no Envio"),
    ]

    veiculo = models.ForeignKey(
        VeiculoIpiranga, on_delete=models.CASCADE, related_name="certificados"
    )
    nome = models.CharField(max_length=255)
    arquivo = models.FileField(
        upload_to="certificados_veiculos/", storage=original_filename_storage
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.veiculo.placa}"  # type: ignore
