# Este script é usado para gerar dados de teste.
# Recomenda-se movê-lo para um diretório 'scripts/' ou 'utils/' para melhor organização.

import cProfile
import os
import pstats
import random
import string
import sys
from io import StringIO

import django
import fitz  # Import PyMuPDF # type: ignore
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.automacao_ipiranga.models import (  # noqa: E402
    CertificadoVeiculo,
    VeiculoIpiranga,
)

# Adicione o decorador @profile para line_profiler
try:
    from line_profiler import LineProfiler
except ImportError:
    LineProfiler = None

if LineProfiler:
    profiler = LineProfiler()
    # Decorar a função run com o profiler
    # Isso será feito manualmente no uso, pois o decorador não pode ser adicionado via script facilmente
    # @profiler
    pass


def run():
    """Cria dados de teste para o projeto Orchestra."""
    # Generate a unique renavam
    unique_renavam = "".join(random.choices("0123456789", k=11))
    # Generate a unique placa
    unique_placa = "".join(random.choices(string.ascii_uppercase, k=3)) + "".join(
        random.choices(string.digits, k=4)
    )

    veiculo = VeiculoIpiranga.objects.create(placa=unique_placa, renavam=unique_renavam)  # type: ignore
    certificado = CertificadoVeiculo.objects.create(  # type: ignore
        veiculo=veiculo,
        nome="CERTIFICADO_TESTE",
        arquivo="certificados_veiculos/test_file.pdf",
        status="pendente",
    )
    # Ensure the directory exists
    pdf_dir = os.path.join(settings.MEDIA_ROOT, "certificados_veiculos")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "test_file.pdf")

    # Create a minimal valid PDF file using PyMuPDF
    doc: fitz.Document = fitz.open()
    doc.new_page()  # type: ignore
    doc.save(pdf_path)
    doc.close()

    print(f"Certificado ID: {certificado.id}")  # type: ignore


if __name__ == "__main__":
    if "--profile-cprofile" in sys.argv:
        print("Executando com cProfile...")
        profiler = cProfile.Profile()
        profiler.enable()
        run()
        profiler.disable()
        s = StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    elif "--profile-line" in sys.argv and LineProfiler:
        print("Executando com line_profiler...")
        # Para line_profiler, a função 'run' precisa ser decorada.
        # Como não podemos decorar dinamicamente, vamos chamar o profiler diretamente.
        # O ideal é adicionar @profile acima da função run() e executar com kernprof -l create_test_data.py
        # Para este exemplo, vamos apenas demonstrar a chamada.
        # Para uso real, adicione @profile à função run() e execute:
        # kernprof -l create_test_data.py
        # python -m line_profiler create_test_data.py.lprof
        print("Para usar line_profiler, adicione @profile à função 'run()' e execute:")
        print("kernprof -l create_test_data.py")
        print("python -m line_profiler create_test_data.py.lprof")
        run()  # Apenas para que a função seja executada
    else:
        run()
