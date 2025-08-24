"""Views para o aplicativo dashboard."""

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga
from apps.common.services import (
    extract_certificate_data_from_filename,
)  # Importar a função

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
            logger.debug(
                f"[POST] Tentando extrair placa e tipo de licença de: {file_name}"
            )

            placa: str | None = None
            nome_certificado: str | None = None
            status: str = "erro"

            try:
                # Extrai todos os dados necessários do nome do arquivo
                # Esta função já valida o formato e levanta ValueError se inválido
                extracted_data = extract_certificate_data_from_filename(
                    file_name, logger
                )
                placa = extracted_data.placa
                nome_certificado = extracted_data.tipo_licenca
                numero_certificado = extracted_data.numero_certificado
                vencimento_valor_portal = extracted_data.data_vencimento_formatada

                logger.info(
                    f"[POST] Placa extraída: {placa}, Tipo de Licença (Certificado): {nome_certificado}"
                )

                logger.debug(
                    f"[POST] Tentando obter ou criar VeiculoIpiranga com placa: {placa}"
                )
                veiculo: VeiculoIpiranga  # type: ignore[reportUnknownVariableType]
                created_veiculo: bool
                veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(  # type: ignore[reportUnknownMemberType]
                    placa=placa, defaults={}
                )
                logger.debug(
                    f"[POST] Resultado VeiculoIpiranga: veiculo={veiculo.placa}, created={created_veiculo}"  # type: ignore[reportUnknownMemberType]
                )

                certificado: CertificadoVeiculo = CertificadoVeiculo.objects.create(  # type: ignore[reportAssignmentType]
                    veiculo=veiculo,
                    nome=nome_certificado,
                    arquivo=uploaded_file,
                    status="pendente",
                )
                logger.info(
                    f"[POST] Novo CertificadoVeiculo criado. ID: {certificado.id}"
                )

                logger.info(
                    f"[POST] Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}"
                )
                status = f"Certificado {nome_certificado} para {placa} salvo com ID: {certificado.id} e status: {certificado.status}"
                logger.info(f"[POST] Status final do certificado: {status}")

                processed_info.append({
                    "id": certificado.id if certificado else None,
                    "file_name": file_name,
                    "placa": placa,
                    "nome_certificado": nome_certificado,
                    "status": status,
                    "numero_certificado": numero_certificado,
                    "vencimento_valor_portal": vencimento_valor_portal,
                })

            except ValueError as ve:
                logger.warning(f"[POST] Erro de validação do nome do arquivo: {ve}")
                processed_info.append({
                    "id": None,
                    "file_name": file_name,
                    "placa": None,
                    "nome_certificado": None,
                    "status": "erro_validacao",
                    "error_message": str(ve),
                })
            except Exception as e:
                error_msg = f"Erro CRÍTICO ao salvar certificado no banco de dados: {e}"
                logger.critical(f"[POST] {error_msg}", exc_info=True)
                processed_info.append({
                    "id": None,
                    "file_name": file_name,
                    "placa": placa,
                    "nome_certificado": nome_certificado,
                    "status": "erro_interno",
                    "error_message": error_msg,
                })

        logger.info("[POST] Processamento de arquivos concluído.")
        return JsonResponse({
            "message": "Processamento de arquivos iniciado.",
            "details": processed_info,
        })
    else:
        logger.warning(
            "[%s] Método não permitido para process_documents_view.", request.method
        )
        return JsonResponse({"error": "Método não permitido."}, status=405)


def check_certificate_status_view(
    request: HttpRequest, certificate_id: int
) -> JsonResponse:
    """Retorna o status de um CertificadoVeiculo."""
    certificado: CertificadoVeiculo | None = None
    try:
        certificado = CertificadoVeiculo.objects.get(pk=certificate_id)  # type: ignore[reportAssignmentType]
        response_data: dict[str, Any] = {
            "id": certificado.id if certificado else None,
            "status": certificado.status if certificado else None,
            "error_message": certificado.error_message
            if certificado
            else None
            if certificado and certificado.error_message
            else "",
            "placa": certificado.veiculo.placa
            if certificado and certificado.veiculo
            else None,
        }
        return JsonResponse(response_data)
    except CertificadoVeiculo.DoesNotExist:
        return JsonResponse({"error": "Certificado não encontrado."}, status=404)
    except Exception as e:
        logger.error(
            f"Erro ao buscar status do certificado {certificate_id}: {e}", exc_info=True
        )
        return JsonResponse({"error": "Erro interno do servidor."}, status=500)
