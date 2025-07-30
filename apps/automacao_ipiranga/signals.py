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
        
        # Inicia o processo em segundo plano, capturando stdout e stderr
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Não espera o processo terminar, mas imprime o PID para referência
        print(f"[DEBUG SIGNAL] Automação para Certificado ID {instance_id} iniciada em segundo plano. PID: {process.pid}")

        # Adicionar um pequeno delay e tentar ler a saída de erro inicial
        time.sleep(1) # Dá um tempo para o subprocesso iniciar e gerar alguma saída
        stdout, stderr = process.communicate(timeout=5) # Tenta ler a saída, com timeout

        if stdout:
            print(f"[DEBUG SIGNAL] STDOUT do subprocesso:\n{stdout.decode()}")
        if stderr:
            print(f"[DEBUG SIGNAL] STDERR do subprocesso:\n{stderr.decode()}")

    except subprocess.TimeoutExpired:
        print(f"[DEBUG SIGNAL] Subprocesso para Certificado ID {instance_id} não respondeu em 5 segundos. Pode estar rodando em background.")
    except Exception as e:
        print(f"[DEBUG SIGNAL] Erro CRÍTICO ao iniciar a automação para o Certificado ID {instance_id}: {e}")

@receiver(post_save, sender=CertificadoVeiculo)
def trigger_automacao_certificado(sender, instance, created, **kwargs):
    """
    Este sinal é acionado sempre que um objeto CertificadoVeiculo é salvo.
    """
    if created and instance.status == 'pendente':
        print(f"[DEBUG SIGNAL] Sinal recebido: Novo CertificadoVeiculo (ID: {instance.id}) com status 'pendente'.")
        run_automation_command(instance.id)
    else:
        print(f"[DEBUG SIGNAL] Sinal recebido para CertificadoVeiculo (ID: {instance.id}), mas não atendeu aos critérios (created={created}, status={instance.status}).")
