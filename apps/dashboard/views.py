import logging
import re

from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def orchestra_view(request):
    """Renderiza a página principal do dashboard."""
    return render(request, "dashboard/orchestra.html", {})


def process_documents_view(request):
    """Processa o upload de documentos, extrai informações e salva no banco de dados."""
    from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

    if request.method == "POST":
        uploaded_files = request.FILES.getlist("documents")

        if not uploaded_files:
            return JsonResponse({"error": "Nenhum arquivo enviado."}, status=400)

        processed_info = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            match = re.match(r"([A-Z0-9]+)_([A-Z_]+)", file_name, re.IGNORECASE)

            placa = None
            nome_certificado = None

            if match:
                placa = match.group(1).upper()
                nome_certificado = (
                    match.group(2).replace("_", " ").title()
                )  # Formata para leitura

                try:
                    # 1. Obter ou criar o VeiculoIpiranga
                    veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(  # type: ignore
                        placa=placa, defaults={}
                    )
                    if created_veiculo:
                        logger.info(f"Veículo {placa} criado no banco de dados.")
                    else:
                        logger.info(f"Veículo {placa} já existe no banco de dados.")

                    # 2. Criar o CertificadoVeiculo e anexar o arquivo
                    # O status inicial é 'pendente', o que acionará o sinal
                    certificado = CertificadoVeiculo.objects.create(  # type: ignore
                        veiculo=veiculo,
                        nome=nome_certificado,
                        arquivo=uploaded_file,  # O arquivo é salvo automaticamente aqui
                        status="pendente",
                    )
                    logger.info(
                        f"Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}"  # type: ignore
                    )
                    status = f"Certificado {nome_certificado} para {placa} salvo com ID: {certificado.id} e status: {certificado.status}"  # type: ignore
                    logger.info(status)

                except Exception as e:
                    status = f"Erro ao salvar certificado no banco de dados: {e}"
                    logger.error(f"Erro ao salvar certificado: {e}")
            else:
                return JsonResponse(
                    {
                        "error": "Nome de arquivo fora do padrão esperado (PLACA_NOME_CERTIFICADO.pdf)."
                    },
                    status=400,
                )

            processed_info.append(
                {
                    "file_name": file_name,
                    "placa": placa,
                    "nome_certificado": nome_certificado,
                    "status": status,
                }
            )

        return JsonResponse(
            {
                "message": "Processamento de arquivos iniciado.",
                "details": processed_info,
            }
        )
    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)
