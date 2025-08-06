import logging
import re

from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def orchestra_view(request):
    """Renderiza a página principal do dashboard."""
    return render(request, "dashboard/orchestra.html", {})


def process_documents_view(request):
    """Processa o upload de documentos e inicia a automação."""
    logger.info(f"[POST] process_documents_view foi chamada. Método: {request.method}")
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
            logger.debug(f"[POST] Tentando extrair placa e certificado de: {file_name}")
            match = re.match(r"([A-Z0-9]+)_([A-Z_]+)", file_name, re.IGNORECASE)

            placa = None
            nome_certificado = None

            if match:
                placa = match.group(1).upper()
                nome_certificado = (
                    match.group(2).replace("_", " ").title()
                )  # Formata para leitura
                logger.info(
                    f"[POST] Placa extraída: {placa}, Certificado extraído: {nome_certificado}"
                )

                try:
                    logger.debug(
                        f"[POST] Tentando obter ou criar VeiculoIpiranga com placa: {placa}"
                    )
                    # 1. Obter ou criar o VeiculoIpiranga
                    veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(  # type: ignore
                        placa=placa, defaults={}
                    )
                    logger.debug(
                        f"[POST] Resultado VeiculoIpiranga: veiculo={veiculo.placa}, created={created_veiculo}"
                    )

                    logger.debug(
                        f"[POST] Tentando criar CertificadoVeiculo para {placa} - {nome_certificado}"
                    )
                    logger.debug(
                        f"[POST] Detalhes do uploaded_file: name={uploaded_file.name}, size={uploaded_file.size}, content_type={uploaded_file.content_type}"
                    )
                    try:
                        # Tenta ler uma pequena parte do arquivo para verificar se está acessível
                        uploaded_file.seek(0)  # Garante que o ponteiro está no início
                        sample_content = uploaded_file.read(100)
                        logger.debug(
                            f"[POST] Amostra do conteúdo do uploaded_file (primeiros 100 bytes): {sample_content[:50]}..."
                        )
                        uploaded_file.seek(
                            0
                        )  # Volta o ponteiro para o início para o FileField
                    except Exception as e:
                        logger.error(f"[POST] Erro ao tentar ler uploaded_file: {e}")
                        raise  # Re-levanta a exceção para que o processo falhe e possamos depurar

                    # 2. Criar o CertificadoVeiculo e anexar o arquivo
                    # O status inicial é 'pendente', o que acionará o sinal
                    certificado = CertificadoVeiculo.objects.create(  # type: ignore
                        veiculo=veiculo,
                        nome=nome_certificado,
                        arquivo=uploaded_file,  # O arquivo é salvo automaticamente aqui
                        status="pendente",
                    )
                    logger.debug(
                        f"[POST] CertificadoVeiculo criado com sucesso. ID: {certificado.id}"
                    )
                    logger.info(
                        f"[POST] Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}"  # type: ignore
                    )
                    status = f"Certificado {nome_certificado} para {placa} salvo com ID: {certificado.id} e status: {certificado.status}"  # type: ignore
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
