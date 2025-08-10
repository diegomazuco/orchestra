# Este script é usado para gerar dados de teste.
# Recomenda-se movê-lo para um diretório 'scripts/' ou 'utils/' para melhor organização.


import os
import sys

# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import django
import fitz  # Import PyMuPDF # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


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
