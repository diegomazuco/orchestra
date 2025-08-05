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
    logger.debug(
        "[%s] Requisição recebida para process_documents_view.", request.method
    )
    from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

    if request.method == "POST":
        logger.debug("[POST] Iniciando processamento de arquivos.")
        uploaded_files = request.FILES.getlist("documents")

        if not uploaded_files:
            logger.warning("[POST] Nenhum arquivo enviado.")
            return JsonResponse({"error": "Nenhum arquivo enviado."}, status=400)

        processed_info = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            logger.info(f"[POST] Processando arquivo: {file_name}")
            match = re.match(r"([A-Z0-9]+)_([A-Z_]+)", file_name, re.IGNORECASE)

            placa = None
            nome_certificado = None

            if match:
                placa = match.group(1).upper()
                nome_certificado = (
                    match.group(2).replace("_", " ").title()
                )  # Formata para leitura
                logger.info(f"[POST] Placa: {placa}, Certificado: {nome_certificado}")

                try:
                    # 1. Obter ou criar o VeiculoIpiranga
                    veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(  # type: ignore
                        placa=placa, defaults={}
                    )
                    if created_veiculo:
                        logger.info(f"[POST] Veículo {placa} criado no banco de dados.")
                    else:
                        logger.info(
                            f"[POST] Veículo {placa} já existe no banco de dados."
                        )

                    # 2. Criar o CertificadoVeiculo e anexar o arquivo
                    # O status inicial é 'pendente', o que acionará o sinal
                    certificado = CertificadoVeiculo.objects.create(  # type: ignore
                        veiculo=veiculo,
                        nome=nome_certificado,
                        arquivo=uploaded_file,  # O arquivo é salvo automaticamente aqui
                        status="pendente",
                    )
                    logger.info(
                        f"[POST] Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}"  # type: ignore
                    )
                    status = f"Certificado {nome_certificado} para {placa} salvo com ID: {certificado.id} e status: {certificado.status}"  # type: ignore
                    logger.info(f"[POST] Status final do certificado: {status}")

                except Exception as e:
                    status = f"Erro ao salvar certificado no banco de dados: {e}"
                    logger.error(
                        f"[POST] Erro ao salvar certificado: {e}", exc_info=True
                    )
            else:
                logger.warning("[POST] Nome de arquivo fora do padrão esperado.")
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

        logger.info("[POST] Processamento de arquivos concluído.")
        return JsonResponse(
            {
                "message": "Processamento de arquivos iniciado.",
                "details": processed_info,
            }
        )
    else:
        logger.warning(
            "[%s] Método não permitido para process_documents_view.", request.method
        )
        return JsonResponse({"error": "Método não permitido."}, status=405)
