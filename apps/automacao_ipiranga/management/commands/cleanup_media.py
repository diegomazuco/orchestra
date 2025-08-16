import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.automacao_ipiranga.models import CertificadoVeiculo


class Command(BaseCommand):
    """Deletes all files from the media/certificados_veiculos folder and CertificadoVeiculo records from the database."""

    help = "Deleta todos os arquivos da pasta media/certificados_veiculos e os registros de CertificadoVeiculo no banco de dados."

    def handle(self, *args: Any, **options: Any) -> None:
        """Handles the command execution to clean up media files and database records."""
        # Deletar registros do banco de dados e arquivos associados
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando a limpeza de registros de CertificadoVeiculo e arquivos associados..."
            )
        )
        certificados = CertificadoVeiculo.objects.all()
        for certificado in certificados:
            if certificado.arquivo and os.path.isfile(certificado.arquivo.path):
                os.remove(certificado.arquivo.path)
                self.stdout.write(
                    self.style.SUCCESS(f"Arquivo {certificado.arquivo.path} deletado.")
                )
            certificado_id: Any = certificado.id  # type: ignore
            certificado.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Registro de certificado {certificado_id} deletado."
                )
            )

        # Deletar todos os arquivos restantes na pasta
        media_path = os.path.join(settings.MEDIA_ROOT, "certificados_veiculos")
        if os.path.exists(media_path):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Iniciando a limpeza de arquivos órfãos em {media_path}..."
                )
            )
            for filename in os.listdir(media_path):
                file_path = os.path.join(media_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.stdout.write(
                        self.style.SUCCESS(f"Arquivo órfão {file_path} deletado.")
                    )

        self.stdout.write(self.style.SUCCESS("Limpeza concluída."))
