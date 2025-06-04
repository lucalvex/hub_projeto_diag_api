import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.http import JsonResponse
from users.models import UserAccount
from .models import Modulo, Dimensao, Pergunta, RespostaDimensao, RespostaModulo
from django.shortcuts import get_object_or_404
import json
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.utils import ImageReader


class QuestionarioView(APIView):
    # Permite não estar autenticado para testes
    permission_classes = [AllowAny]

    def get(self, request):
        try:

            modulos = Modulo.objects.prefetch_related(
                'dimensoes__perguntas').all()

            dadosQuestionario = []

            for modulo in modulos:
                dimensoesDoModulo = modulo.dimensoes.all()
                dadosDimensoes = []

                for dimensao in dimensoesDoModulo:

                    dadosDimensao = {
                        'dimensaoTitulo': dimensao.titulo,
                        'descricao': dimensao.descricao,
                        'tipo': dimensao.get_tipo_display(),
                        'explicacao': dimensao.explicacao,
                    }
                    dadosDimensoes.append(dadosDimensao)

                dadosModulo = {
                    'nome': modulo.nome,
                    'descricao': modulo.descricao,
                    'tempo': modulo.tempo,
                    'perguntasQntd': modulo.perguntasQntd,
                    'dimensoes': dadosDimensoes
                }
                dadosQuestionario.append(dadosModulo)

            return Response({'modulos': dadosQuestionario})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModuloView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, nomeModulo):
        try:
            moduloObj = get_object_or_404(
                Modulo.objects.prefetch_related('dimensoes__perguntas'),
                nome=nomeModulo
            )

            dadosDimensoes = []

            for dimensao in moduloObj.dimensoes.all():
                perguntasData = []
                for p in dimensao.perguntas.all():
                    perguntasData.append({
                        'id': p.id,
                        'pergunta': p.pergunta,
                    })

                dados_dimensao = {
                    'dimensaoTitulo': dimensao.titulo,
                    'descricao': dimensao.descricao,
                    'tipo': dimensao.get_tipo_display(),
                    'explicacao': dimensao.explicacao,
                    'perguntas': perguntasData
                }
                dadosDimensoes.append(dados_dimensao)

            response_data = {
                'nomeModulo': moduloObj.nome,
                'dimensoes': dadosDimensoes
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Ocorreu um erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SalvarRespostasModuloView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, nomeModulo):
        usuario = request.user
        try:
            modulo = get_object_or_404(Modulo, nome=nomeModulo)
        except Modulo.DoesNotExist:
            return Response(
                {'error': f'Módulo com nome "{nomeModulo}" não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        respostasData = request.data.get('respostas')

        if respostasData is None:
            return Response(
                {'error': 'Payload deve conter a chave "respostas".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(respostasData, list):
            return Response(
                {'error': '"respostas" deve ser uma lista.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not respostasData:
            return Response(
                {'warning': 'A lista "respostas" está vazia. Nenhuma resposta foi processada.'},
                status=status.HTTP_200_OK
            )

        erros = []
        perguntasRespondidasId = set()
        somasPorDimensao = {}

        try:
            perguntasDoModulo = Pergunta.objects.filter(
                dimensao__modulo=modulo
            ).select_related('dimensao')
            mapa_perguntas_validas = {p.id: p for p in perguntasDoModulo}
        except Exception as e:
            return Response(
                {'error': f'Erro crítico ao buscar perguntas do módulo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        for idx, resposta_info in enumerate(respostasData):
            if not isinstance(resposta_info, dict):
                erros.append(f"Item {idx+1}: Não é um objeto JSON válido.")
                continue

            perguntaId = resposta_info.get('perguntaId')
            valor = resposta_info.get('valor')

            if perguntaId is None:
                erros.append(f"Item {idx+1}: Chave 'perguntaId' ausente.")
                continue
            if valor is None:
                erros.append(
                    f"Item {idx+1} (Pergunta ID {perguntaId}): Chave 'valor' ausente.")
                continue

            try:
                valor_int = int(valor)
            except (ValueError, TypeError):
                erros.append(
                    f"Item {idx+1} (Pergunta ID {perguntaId}): 'valor' deve ser um número inteiro (recebeu '{valor}').")
                continue

            perguntaObj = mapa_perguntas_validas.get(perguntaId)
            if not perguntaObj:
                erros.append(
                    f"Item {idx+1}: Pergunta com ID {perguntaId} não encontrada ou não pertence ao módulo '{nomeModulo}'.")
                continue

            if perguntaId in perguntasRespondidasId:
                erros.append(
                    f"Item {idx+1}: Resposta duplicada para a pergunta com ID {perguntaId} nesta requisição.")
                continue
            perguntasRespondidasId.add(perguntaId)

            dimensaoObj = perguntaObj.dimensao
            dimensaoPk = dimensaoObj.pk
            valorPonderado = valor_int * perguntaObj.peso
            somasPorDimensao[dimensaoPk] = somasPorDimensao.get(
                dimensaoPk, 0) + valorPonderado

        if erros:
            return Response({
                'error': 'Falha na validação das respostas. Nenhuma resposta foi salva.',
                'detalhes': erros,
            }, status=status.HTTP_400_BAD_REQUEST)

        dimensoesAtualizadas = []
        respostaModuloStatus = None
        valorFinalModulo = 0

        try:
            for dimensaoPk, somaTotal in somasPorDimensao.items():
                respostaDimensaoObj, created = RespostaDimensao.objects.update_or_create(
                    usuario=usuario,
                    dimensao_id=dimensaoPk,
                    defaults={'valorFinal': somaTotal}
                )
                dimensoesAtualizadas.append({
                    'dimensaoId': dimensaoPk,
                    'tituloDimensao': respostaDimensaoObj.dimensao.titulo,
                    'valorFinal': somaTotal,
                    'status': 'Criada' if created else 'Atualizada'
                })

            valorFinalModulo = sum(somasPorDimensao.values())

            respostaModuloObj, created_modulo = RespostaModulo.objects.update_or_create(
                usuario=usuario,
                modulo=modulo,
                defaults={'valorFinal': valorFinalModulo}
            )
            respostaModuloStatus = 'Criada' if created_modulo else 'Atualizada'

        except Exception as e:
            return Response(
                {'error': f'Erro ao salvar respostas no banco de dados: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                'message': f'Respostas para o módulo "{nomeModulo}" processadas e salvas com sucesso.',
                'modulo': {
                    'moduloId': modulo.id,
                    'nomeModulo': modulo.nome,
                    'valorFinal': valorFinalModulo,
                    'status': respostaModuloStatus
                },
                'dimensoesAtualizadas': dimensoesAtualizadas
            },
            status=status.HTTP_200_OK
        )

class GerarRelatorioModuloView(APIView):
    permission_classes = [IsAuthenticated]

    def _avaliar_modulo(self, pontuacao):
        if 142 <= pontuacao <= 175:
            return "Excelente"
        elif 106 <= pontuacao <= 141:
            return "Ótimo"
        elif 71 <= pontuacao <= 105:
            return "Médio"
        elif 35 <= pontuacao <= 70:
            return "Insuficiente"
        else:
            return "Fora da faixa de avaliação"

    def _avaliar_dimensao(self, pontuacao):
        if 21 <= pontuacao <= 25:
            return "Excelente"
        elif 16 <= pontuacao <= 20:
            return "Ótimo"
        elif 11 <= pontuacao <= 15:
            return "Médio"
        elif 5 <= pontuacao <= 10:
            return "Insuficiente"
        else:
            return "Fora da faixa de avaliação"

    def get(self, request, nomeModulo):
        usuario = request.user

        try:
            modulo = get_object_or_404(Modulo, nome=nomeModulo)

            resposta_modulo = get_object_or_404(
                RespostaModulo, usuario=usuario, modulo=modulo
            )

            respostas_dimensoes = RespostaDimensao.objects.filter(
                usuario=usuario,
                dimensao__modulo=modulo
            ).select_related('dimensao').order_by('dimensao__titulo')

            if not respostas_dimensoes.exists():
                 return Response(
                     {'error': f'Respostas das dimensões para o módulo "{nomeModulo}" não encontradas para este usuário.'},
                     status=status.HTTP_404_NOT_FOUND
                 )

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            width, height = A4

            y_position = height - 1.5*cm
            margin_left = 1.5*cm
            content_width = width - 2*margin_left

            style_title = styles['h1']
            style_h2 = styles['h2']
            style_body = styles['BodyText']
            style_body.leading = 14

            p = Paragraph("Relatório de Desempenho", style_title)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.5*cm)

            p = Paragraph(f"<b>Usuário:</b> {usuario.username} ({usuario.email})", style_body)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.2*cm)

            p = Paragraph(f"<b>Módulo:</b> {modulo.nome}", style_h2)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.1*cm)

            p = Paragraph(f"<i>Descrição:</i> {modulo.descricao}", style_body)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.5*cm)

            pontuacao_modulo = resposta_modulo.valorFinal
            avaliacao_modulo = self._avaliar_modulo(pontuacao_modulo)
            p = Paragraph(f"<b>Resultado Geral do Módulo:</b> {pontuacao_modulo} pontos - <b>{avaliacao_modulo}</b>", style_body)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.7*cm)

            p = Paragraph("Resultados por Dimensão:", style_h2)
            p.wrapOn(c, content_width, height)
            p_height = p.height
            p.drawOn(c, margin_left, y_position - p_height)
            y_position -= (p_height + 0.3*cm)

            for resp_dim in respostas_dimensoes:
                dimensao = resp_dim.dimensao
                pontuacao_dimensao = resp_dim.valorFinal
                avaliacao_dimensao = self._avaliar_dimensao(pontuacao_dimensao)

                p = Paragraph(f"<b>{dimensao.titulo}:</b>", style_body)
                p.wrapOn(c, content_width, height)
                p_height = p.height
                p.drawOn(c, margin_left, y_position - p_height)
                y_position -= p_height

                p = Paragraph(f"    Pontuação: {pontuacao_dimensao} - <b>{avaliacao_dimensao}</b>", style_body)
                p.wrapOn(c, content_width, height)
                p_height = p.height
                p.drawOn(c, margin_left, y_position - p_height)
                y_position -= (p_height + 0.3*cm)

                if y_position < 3*cm:
                    c.showPage() 
                    y_position = height - 1.5*cm

            img_width = 10 * cm
            img_height = 10 * cm
            x_center = (width - img_width) / 2
            if y_position - img_height < 2*cm:
                c.showPage()
                y_position = height - 2*cm

            labels = [resp.dimensao.titulo for resp in respostas_dimensoes]
            values = [resp.valorFinal for resp in respostas_dimensoes]
            if len(labels) < 3:
                labels += [''] * (3 - len(labels))
                values += [0] * (3 - len(values))
            num_vars = len(labels)

            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.plot(angles, values, color='#4bd360', linewidth=2)
            ax.fill(angles, values, color='#4bd360', alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=10)
            ax.set_yticklabels([])
            ax.set_title('Desempenho por Dimensão', y=1.08)
            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='PNG', bbox_inches='tight', dpi=120)
            plt.close(fig)
            img_buffer.seek(0)
            radar_img = ImageReader(img_buffer)

            c.drawImage(radar_img, x_center, y_position - img_height, width=img_width, height=img_height)
            y_position -= (img_height + 0.5*cm)

            c.save()

            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"relatorio_{nomeModulo.replace(' ', '_')}_{usuario.username}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Modulo.DoesNotExist:
            return Response(
                {'error': f'Módulo com nome "{nomeModulo}" não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except RespostaModulo.DoesNotExist:
             return Response(
                {'error': f'O usuário {usuario.username} ainda não respondeu ao módulo "{nomeModulo}".'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar o relatório PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )