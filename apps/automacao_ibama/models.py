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
        return self.numero