import os
from django.conf import settings
import django
import fitz  # Import PyMuPDF
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.automacao_ipiranga.models import VeiculoIpiranga, CertificadoVeiculo

def run():
    # Generate a unique renavam
    unique_renavam = ''.join(random.choices('0123456789', k=11))
    # Generate a unique placa
    unique_placa = ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

    veiculo = VeiculoIpiranga.objects.create(placa=unique_placa, renavam=unique_renavam)
    certificado = CertificadoVeiculo.objects.create(
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
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()

    print(f'Certificado ID: {certificado.id}')

if __name__ == '__main__':
    run()