import logging
import re
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

logger = logging.getLogger(__name__)


def orchestra_view(request: HttpRequest) -> HttpResponse:
    """Renderiza a página principal do dashboard."""
    return render(request, "dashboard/orchestra.html", {})


def process_documents_view(request: HttpRequest) -> JsonResponse:
    """Processa o upload de documentos e inicia a automação."""
    logger.info(f"[POST] process_documents_view foi chamada. Método: {request.method}")
    logger.debug(
        "[%s] Requisição recebida para process_documents_view.", request.method
    )

    if request.method == "POST":
        logger.debug("[POST] Iniciando processamento de arquivos.")
        uploaded_files: list[Any] = request.FILES.getlist("documents")

        if not uploaded_files:
            logger.warning("[POST] Nenhum arquivo enviado.")
            return JsonResponse({"error": "Nenhum arquivo enviado."}, status=400)

        processed_info: list[dict[str, Any]] = []
        for uploaded_file in uploaded_files:
            file_name: str = uploaded_file.name
            logger.info(f"[POST] Processando arquivo: {file_name}")
            logger.debug(f"[POST] Tentando extrair placa e certificado de: {file_name}")
            match: re.Match[str] | None = re.match(
                r"([A-Z0-9]+)_([A-Z_]+)", file_name, re.IGNORECASE
            )

            placa: str | None = None
            nome_certificado: str | None = None
            status: str = "erro"

            if match:
                placa = match.group(1).upper()
                nome_certificado = match.group(2).replace("_", " ").title()
                logger.info(
                    f"[POST] Placa extraída: {placa}, Certificado extraído: {nome_certificado}"
                )

                try:
                    logger.debug(
                        f"[POST] Tentando obter ou criar VeiculoIpiranga com placa: {placa}"
                    )
                    veiculo: VeiculoIpiranga
                    created_veiculo: bool
                    veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(
                        placa=placa, defaults={}
                    )
                    logger.debug(
                        f"[POST] Resultado VeiculoIpiranga: veiculo={veiculo.placa}, created={created_veiculo}"
                    )

                    certificado: CertificadoVeiculo = CertificadoVeiculo.objects.create(
                        veiculo=veiculo,
                        nome=nome_certificado,  # type: ignore
                        arquivo=uploaded_file,
                        status="pendente",
                    )
                    logger.info(
                        f"[POST] Novo CertificadoVeiculo criado. ID: {certificado.id}"  # type: ignore[reportUnknownMemberType]
                    )

                    logger.info(
                        f"[POST] Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}"  # type: ignore[reportUnknownMemberType]
                    )
                    status = f"Certificado {nome_certificado} para {placa} salvo com ID: {certificado.id} e status: {certificado.status}"  # type: ignore[reportUnknownMemberType]
                    logger.info(f"[POST] Status final do certificado: {status}")

                except Exception as e:
                    status = (
                        f"Erro CRÍTICO ao salvar certificado no banco de dados: {e}"
                    )
                    logger.critical(
                        f"[POST] Erro CRÍTICO ao salvar certificado: {e}", exc_info=True
                    )
            else:
                logger.warning("[POST] Nome de arquivo fora do padrão esperado.")
                return JsonResponse(
                    {
                        "error": "Nome de arquivo fora do padrão esperado (PLACA_NOME_CERTIFICADO.pdf).",
                        "file_name": file_name,
                    },
                    status=400,
                )

            processed_info.append(
                {
                    "file_name": file_name,
                    "placa": placa,  # type: ignore[reportUnknownMemberType]
                    "nome_certificado": nome_certificado,  # type: ignore[reportUnknownMemberType]
                    "status": status,  # type: ignore[reportUnknownMemberType]
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
