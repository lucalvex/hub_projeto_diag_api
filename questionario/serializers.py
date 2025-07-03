from rest_framework import serializers
from .models import RespostaModulo, RespostaDimensao, Modulo, Dimensao

class RelatorioSerializer(serializers.ModelSerializer):
  usuario = serializers.CharField(source='usuario.username', read_only=True)
  nome_modulo = serializers.CharField(source='modulo.nome', read_only=True)
  valorFinal = serializers.IntegerField()
  dataResposta = serializers.DateTimeField(format='%Y-%m-%d')

  class Meta:
    model = RespostaModulo
    fields = ['id', 'usuario', 'nome_modulo', 'valorFinal', 'dataResposta']

class DimensaoSerializer(serializers.ModelSerializer):
  class Meta:
    model = Dimensao
    fields = ['id', 'titulo']

class RespostaDimensaoSerializer(serializers.ModelSerializer):
  dimensao = DimensaoSerializer()

  class Meta:
    model = RespostaDimensao  
    fields = ['dimensao', 'valorFinal']
  
  def get_resposta_modulo(self, obj):
    return {
      'id': obj.resposta_modulo.id,
      'valorFinal': obj.resposta_modulo.valorFinal,
    }

class RespostaModuloSerializer(serializers.ModelSerializer):
  modulo = serializers.SerializerMethodField()
  usuario = serializers.SerializerMethodField()
  dimensoes = serializers.SerializerMethodField()

  class Meta:
    model = RespostaModulo
    fields = ['modulo', 'usuario', 'valorFinal', 'dataResposta', 'dimensoes']

  def get_modulo(self, obj):
    return {
      'nome': obj.modulo.nome,
      'descricao': obj.modulo.descricao
    }

  def get_usuario(self, obj):
    return {
      'username': obj.usuario.username,
      'email': obj.usuario.email
    }

  def get_dimensoes(self, obj):
    resposta_dimensoes = RespostaDimensao.objects.filter(resposta_modulo=obj)
    serializer = RespostaDimensaoSerializer(resposta_dimensoes, many=True)
    return serializer.data
  
  def to_representation(self, instance):
    data = super().to_representation(instance)

    # Aqui você calcula ou injeta a média dos outros usuários
    media_dimensoes = self.context.get('media_dimensoes')
    if media_dimensoes:
      data['media_dimensoes'] = media_dimensoes

    return data
