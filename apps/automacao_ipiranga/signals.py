# import subprocess
# import sys
# import os
# import logging
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import CertificadoVeiculo

# logger = logging.getLogger(__name__)

# def run_automation_command(instance_id):
#     """
#     Executa o comando de automação em um processo separado e robusto,
#     redirecionando a saída para arquivos de log específicos.
#     """
#     try:
#         python_executable = sys.executable
#         manage_py_path = os.path.abspath('./manage.py')
#         project_root = os.path.dirname(manage_py_path)
#
#         # Arquivos de log para o subprocesso
#         stdout_log_path = os.path.join(project_root, 'automation_stdout.log')
#         stderr_log_path = os.path.join(project_root, 'automation_stderr.log')
#
#         command = [
#             python_executable,
#             manage_py_path,
#             'automacao_documentos_ipiranga',
#             str(instance_id)
#         ]
#        
#         logger.info(f"[SIGNAL] Executando comando em subprocesso: {' '.join(command)}")
#         logger.info(f"[SIGNAL] Log de STDOUT será salvo em: {stdout_log_path}")
#         logger.info(f"[SIGNAL] Log de STDERR será salvo em: {stderr_log_path}")
#
#         # Abrir arquivos de log para o subprocesso
#         stdout_log = open(stdout_log_path, 'w')
#         stderr_log = open(stderr_log_path, 'w')
#
#         # Inicia o processo em segundo plano, desanexando-o completamente
#         process = subprocess.Popen(
#             command, 
#             stdout=stdout_log, 
#             stderr=stderr_log, 
#             preexec_fn=os.setsid, # Essencial para desanexar em Unix-like systems
#             cwd=project_root
#         )
#        
#         logger.info(f"[SIGNAL] Automação para Certificado ID {instance_id} iniciada em segundo plano. PID: {process.pid}")
#
#     except Exception as e:
#         logger.error(f"[SIGNAL] Erro CRÍTICO ao iniciar o subprocesso para o Certificado ID {instance_id}: {e}", exc_info=True)
#
# @receiver(post_save, sender=CertificadoVeiculo)
# def trigger_automacao_certificado(sender, instance, created, **kwargs):
#     """
#     Dispara a automação quando um novo CertificadoVeiculo pendente é criado.
#     """
#     logger.info(f"[SIGNAL] Sinal post_save recebido para CertificadoVeiculo ID: {instance.id} (Created: {created}, Status: {instance.status})")
#     if created and instance.status == 'pendente':
#         logger.info(f"[SIGNAL] Condições atendidas. Disparando automação para o Certificado ID: {instance.id}")
#         run_automation_command(instance.id)
#     else:
#         logger.info(f"[SIGNAL] Condições não atendidas. Nenhuma automação foi disparada para o Certificado ID: {instance.id}.")