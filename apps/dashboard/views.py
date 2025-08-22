import logging
import re
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
                # Chamar a função para validar o formato completo e obter os dados
                # Se ela levantar ValueError, será capturado pelo bloco try-except
                # A placa e o tipo de licença (nome do certificado) são extraídos aqui
                # para a criação do CertificadoVeiculo.
                # A automação usará extract_certificate_data_from_filename novamente
                # para obter numero_certificado e data_vencimento_formatada do arquivo.

                # Extrair placa e nome_certificado (tipo de licença) usando regex
                # Este regex deve ser consistente com o esperado por extract_certificate_data_from_filename
                match_data = re.match(
                    r"([A-Z0-9]+)_([A-Z_]+)_([A-Z0-9]+)_(\d{8})\.pdf",
                    file_name,
                    re.IGNORECASE,
                )

                if not match_data:
                    logger.warning(
                        f"[POST] Nome de arquivo fora do padrão esperado: {file_name}"
                    )
                    return JsonResponse(
                        {
                            "error": "Nome de arquivo fora do padrão esperado (PLACA_TIPOLICENCA_NUMEROCERTIFICADO_DDMMYYYY.pdf).",
                            "file_name": file_name,
                        },
                        status=400,
                    )

                placa = match_data.group(1).upper()
                nome_certificado = match_data.group(2).replace("_", " ").title()

                # Chamar a função para validar o formato completo e garantir que ela não levante erro
                # Se ela levantar ValueError, será capturado pelo bloco try-except
                extract_certificate_data_from_filename(
                    file_name, logger
                )  # AQUI ESTÁ A CHAMADA QUE FALTAVA

                logger.info(
                    f"[POST] Placa extraída: {placa}, Tipo de Licença (Certificado): {nome_certificado}"
                )

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
                    nome=nome_certificado,
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

            except ValueError as ve:
                logger.warning(f"[POST] Erro de validação do nome do arquivo: {ve}")
                return JsonResponse(
                    {"error": str(ve), "file_name": file_name}, status=400
                )
            except Exception as e:
                status = f"Erro CRÍTICO ao salvar certificado no banco de dados: {e}"
                logger.critical(
                    f"[POST] Erro CRÍTICO ao salvar certificado: {e}", exc_info=True
                )
                return JsonResponse(
                    {"error": status, "file_name": file_name}, status=500
                )

            processed_info.append(
                {
                    "id": certificado.id,  # type: ignore[reportUnknownMemberType]
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


def check_certificate_status_view(
    request: HttpRequest, certificate_id: int
) -> JsonResponse:
    """Retorna o status de um CertificadoVeiculo."""
    certificado: CertificadoVeiculo | None = None
    try:
        certificado = CertificadoVeiculo.objects.get(pk=certificate_id)
        response_data = {
            "id": certificado.id,  # type: ignore[reportUnknownMemberType]
            "status": certificado.status,
            "error_message": certificado.error_message
            if certificado.error_message
            else "",
            "placa": certificado.veiculo.placa,  # type: ignore[reportUnknownMemberType]
        }
        return JsonResponse(response_data)
    except CertificadoVeiculo.DoesNotExist:
        return JsonResponse({"error": "Certificado não encontrado."}, status=404)
    except Exception as e:
        logger.error(
            f"Erro ao buscar status do certificado {certificate_id}: {e}", exc_info=True
        )
        return JsonResponse({"error": "Erro interno do servidor."}, status=500)
