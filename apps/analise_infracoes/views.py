from django.shortcuts import render

from .models import Infracao


def listar_infracoes(request):
    """View para listar as infrações armazenadas no banco de dados PostgreSQL."""
    infracoes = Infracao.objects.using("postgres_db").all()
    context = {"infracoes": infracoes}
    return render(request, "analise_infracoes/listar_infracoes.html", context)
