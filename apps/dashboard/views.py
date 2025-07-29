from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command # Importar call_command
from django.core.files.storage import default_storage # Para salvar arquivos
from django.conf import settings # Para acessar MEDIA_ROOT
import os
import re

def orchestra_view(request):
    return render(request, 'dashboard/orchestra.html', {})

@csrf_exempt
def process_documents_view(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('documents')

        if not uploaded_files:
            return JsonResponse({'error': 'Nenhum arquivo enviado.'}, status=400)

        # Criar diretório temporário para uploads se não existir
        temp_upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_upload_dir, exist_ok=True)

        processed_info = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            match = re.match(r'([A-Z0-9]+)_([A-Z_]+)', file_name, re.IGNORECASE)

            placa = None
            nome_certificado = None
            temp_file_path = None

            if match:
                placa = match.group(1)
                nome_certificado = match.group(2)
                
                # Salvar o arquivo temporariamente
                temp_file_name = default_storage.save(os.path.join('temp_uploads', uploaded_file.name), uploaded_file)
                temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)

                print(f"Arquivo: {file_name}, Placa: {placa}, Certificado: {nome_certificado}, Caminho Temp: {temp_file_path}")

                try:
                    # Chamar o custom command em um processo separado para não bloquear a requisição
                    # Em produção, considere usar uma fila de tarefas (Celery, etc.)
                    # Para este teste, vamos chamar diretamente, mas esteja ciente das implicações
                    call_command('automacao_documentos_ipiranga', placa, nome_certificado, temp_file_path)
                    status = 'Processado com sucesso'
                except CommandError as e:
                    status = f'Erro na automação: {e}'
                    print(f"Erro ao chamar comando: {e}")
                except Exception as e:
                    status = f'Erro inesperado: {e}'
                    print(f"Erro inesperado: {e}")
            else:
                status = 'Nome de arquivo fora do padrão esperado.'
                print(f"Nome de arquivo fora do padrão esperado: {file_name}")

            processed_info.append({
                'file_name': file_name,
                'placa': placa,
                'nome_certificado': nome_certificado,
                'status': status
            })

        return JsonResponse({'message': 'Processamento de arquivos iniciado.', 'details': processed_info})
    else:
        return JsonResponse({'error': 'Método não permitido.'}, status=405)