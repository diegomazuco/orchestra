from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import re

from apps.automacao_ipiranga.models import VeiculoIpiranga, CertificadoVeiculo

def orchestra_view(request):
    return render(request, 'dashboard/orchestra.html', {})

def process_documents_view(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('documents')

        if not uploaded_files:
            return JsonResponse({'error': 'Nenhum arquivo enviado.'}, status=400)

        processed_info = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            match = re.match(r'([A-Z0-9]+)_([A-Z_]+)', file_name, re.IGNORECASE)

            placa = None
            nome_certificado = None
            
            if match:
                placa = match.group(1).upper()
                nome_certificado = match.group(2).replace('_', ' ').title() # Formata para leitura
                
                try:
                    # 1. Obter ou criar o VeiculoIpiranga
                    veiculo, created_veiculo = VeiculoIpiranga.objects.get_or_create(
                        placa=placa,
                        defaults={'renavam': 'Aguardando'} # Renavam pode ser atualizado depois
                    )
                    if created_veiculo:
                        print(f"Veículo {placa} criado no banco de dados.")
                    else:
                        print(f"Veículo {placa} já existe no banco de dados.")

                    # 2. Criar o CertificadoVeiculo e anexar o arquivo
                    # O status inicial é 'pendente', o que acionará o sinal
                    certificado = CertificadoVeiculo.objects.create(
                        veiculo=veiculo,
                        nome=nome_certificado,
                        arquivo=uploaded_file, # O arquivo é salvo automaticamente aqui
                        status='pendente'
                    )
                    print(f"Certificado {nome_certificado} para {placa} salvo. ID: {certificado.id}")
                    status = 'Processamento iniciado com sucesso!'

                except Exception as e:
                    status = f'Erro ao salvar certificado no banco de dados: {e}'
                    print(f"Erro ao salvar certificado: {e}")
            else:
                status = 'Nome de arquivo fora do padrão esperado (PLACA_NOME_CERTIFICADO.pdf).'
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