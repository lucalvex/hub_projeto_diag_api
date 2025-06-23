from rest_framework import serializers
from .models import RespostaDimensao

class RelatorioSerializer(serializers.ModelSerializer):
  class Meta:
    model = RespostaDimensao
    fields = ['id', 'usuario', 'valorFinal', 'datResposta', 'dimensao']