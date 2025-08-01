# Este script é usado para gerar dados de teste.
# Recomenda-se movê-lo para um diretório 'scripts/' ou 'utils/' para melhor organização.

import os
import random
import string

import django
import fitz  # Import PyMuPDF
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.automacao_ipiranga.models import (  # noqa: E402
    CertificadoVeiculo,
    VeiculoIpiranga,
)


def run():
    # Generate a unique renavam
    unique_renavam = ''.join(random.choices('0123456789', k=11))
    # Generate a unique placa
    unique_placa = ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

    veiculo = VeiculoIpiranga.objects.create(placa=unique_placa, renavam=unique_renavam)  # type: ignore
    certificado = CertificadoVeiculo.objects.create(  # type: ignore
        veiculo=veiculo,
        nome='CERTIFICADO_TESTE',
        arquivo='certificados_veiculos/test_file.pdf',
        status='pendente'
    )
    # Ensure the directory exists
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'certificados_veiculos')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, 'test_file.pdf')

    # Create a minimal valid PDF file using PyMuPDF
    doc: fitz.Document = fitz.open()
    doc.new_page()  # type: ignore
    doc.save(pdf_path)
    doc.close()

    print(f'Certificado ID: {certificado.id}')

if __name__ == '__main__':
    run()
