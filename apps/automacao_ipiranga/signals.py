# apps/automacao_ipiranga/signals.py

import subprocess
import sys
import os
import time # Importar time para um pequeno delay
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CertificadoVeiculo

def run_automation_command(instance_id):
    """
    Função para executar o comando de automação em um processo separado.
    Captura stdout e stderr para depuração.
    """
    try:
        python_executable = sys.executable
        manage_py_path = os.path.abspath('./manage.py') # Garante caminho absoluto
        
        command = [
            python_executable,
            manage_py_path,
            'automacao_documentos_ipiranga',
            str(instance_id)
        ]
        
        print(f"[DEBUG SIGNAL] Tentando executar comando: {' '.join(command)}")
        
        # Inicia o processo em segundo plano, desanexando-o do processo pai
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
        
        # Não espera o processo terminar, mas imprime o PID para referência
        print(f"[DEBUG SIGNAL] Automação para Certificado ID {instance_id} iniciada em segundo plano. PID: {process.pid}")
        sys.stdout.flush()
        sys.stderr.flush()

    except Exception as e:
        print(f"[DEBUG SIGNAL] Erro CRÍTICO ao iniciar a automação para o Certificado ID {instance_id}: {e}")

@receiver(post_save, sender=CertificadoVeiculo)
def trigger_automacao_certificado(sender, instance, created, **kwargs):
    """
    Este sinal é acionado sempre que um objeto CertificadoVeiculo é salvo.
    """
    print(f"[DEBUG SIGNAL] Sinal post_save recebido para CertificadoVeiculo ID: {instance.id}")
    print(f"[DEBUG SIGNAL] created: {created}, instance.status: {instance.status}")
    if created and instance.status == 'pendente':
        print(f"[DEBUG SIGNAL] Condições atendidas: Disparando automação para Certificado ID: {instance.id}")
        run_automation_command(instance.id)
    else:
        print(f"[DEBUG SIGNAL] Condições NÃO atendidas para Certificado ID: {instance.id}. Não disparando automação.")
