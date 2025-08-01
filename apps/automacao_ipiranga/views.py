import json

from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def iniciar_automacao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            certificado_id = data.get('certificado_id')

            if certificado_id is None:
                return JsonResponse({'status': 'erro', 'message': 'ID do certificado não fornecido.'}, status=400)

            # Chamar o comando Django em um processo separado para não bloquear a requisição web
            # e permitir que a automação com Playwright seja executada.
            # NOTA: Em um ambiente de produção, considere usar um sistema de filas (ex: Celery) para tarefas longas.
            call_command('automacao_documentos_ipiranga', str(certificado_id))

            return JsonResponse({'status': 'sucesso', 'message': f'Automação iniciada para o certificado ID: {certificado_id}'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'erro', 'message': 'Requisição inválida. JSON esperado.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'erro', 'message': 'Método não permitido.'}, status=405)
