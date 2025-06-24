from rest_framework import serializers
from .models import RespostaModulo


class RelatorioSerializer(serializers.ModelSerializer):
  usuario = serializers.CharField(source='usuario.username', read_only=True)
  nome_modulo = serializers.CharField(source='modulo.nome', read_only=True)
  valorFinal = serializers.IntegerField()
  dataResposta = serializers.DateTimeField(format='%Y-%m-%d')

  class Meta:
    model = RespostaModulo
    fields = ['id', 'usuario', 'nome_modulo', 'valorFinal', 'dataResposta']