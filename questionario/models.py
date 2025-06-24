from django.db import models
from users.models import UserAccount


class Relatorio(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    PATH = models.FileField(max_length=255)

    def __str__(self):
        return f"Relatório {self.id} - {self.data.strftime('%Y-%m-%d')}"


class Modulo(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.TextField()
    perguntasQntd = models.IntegerField(default=0)
    tempo = models.IntegerField(default=0)  # minutos

    def __str__(self):
        return self.nome


class RespostaModulo(models.Model):
    usuario = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    modulo = models.ForeignKey(
        Modulo, on_delete=models.CASCADE, related_name='respostas', default=None)
    valorFinal = models.IntegerField(default=0)
    dataResposta = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Respostas dos Módulos'


class Dimensao(models.Model):
    TIPO_CHOICES = [
        ('OBRIGATORIO', 'Obrigatório'),
        ('COMERCIO', 'Comércio'),
        ('SERVICO', 'Serviço'),
        ('INDUSTRIA', 'Indústria'),
    ]

    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255, unique=True)
    descricao = models.TextField()
    explicacao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    modulo = models.ForeignKey(
        Modulo, on_delete=models.CASCADE, related_name='dimensoes')

    def __str__(self):
        return self.titulo


class RespostaDimensao(models.Model):
    usuario = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    valorFinal = models.IntegerField(default=0)
    dataResposta = models.DateTimeField(auto_now=True)
    dimensao = models.ForeignKey(
        Dimensao, on_delete=models.CASCADE, related_name='respostas', default=None)

    class Meta:
        unique_together = ('usuario', 'dimensao')
        verbose_name_plural = 'Respostas das Dimensões'


class Pergunta(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta = models.TextField()
    peso = models.IntegerField(default=1)
    dimensao = models.ForeignKey(
        Dimensao, on_delete=models.CASCADE, related_name='perguntas', default=None)
