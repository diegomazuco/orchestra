from django.db import models

class LicencaAmbiental(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente de Envio'),
        ('enviado', 'Enviado com Sucesso'),
        ('falha', 'Falha no Envio'),
    ]

    numero = models.CharField(max_length=255, unique=True)
    descricao = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to='licencas/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.numero)

class Portal(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    url_base = models.URLField()
    usuario = models.CharField(max_length=255, blank=True, null=True)
    senha = models.CharField(max_length=255, blank=True, null=True) # Em produção, usar gerenciador de segredos

    def __str__(self):
        return str(self.nome) # type: ignore

class Automacao(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE)
    ultima_execucao = models.DateTimeField(null=True, blank=True)
    proxima_execucao = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True) # type: ignore[reportArgumentType]

    def __str__(self):
        return str(self.nome)

class LogExecucaoAutomacao(models.Model):
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('falha', 'Falha'),
        ('alerta', 'Alerta'),
    ]

    automacao = models.ForeignKey(Automacao, on_delete=models.CASCADE)
    data_execucao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    mensagem = models.TextField(blank=True, null=True)
    dados_coletados = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Log de {self.automacao.nome if self.automacao else 'N/A'} em {self.data_execucao.strftime('%Y-%m-%d %H:%M') if self.data_execucao else 'N/A'}" # type: ignore
