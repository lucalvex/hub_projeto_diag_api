from django.urls import path
from .views import (
    QuestionarioView,
    SalvarRespostasModuloView,
    ModuloView,
    GerarRelatorioModuloView,
    SearchRelatorio,
    CheckDeadlineResponde,
    SearchAllDatesRelatorio,
    SearchLastDimensaoResultados,
    RespostaModuloViewSet,
    SalvarRespostaIncompletaView
)

urlpatterns = [
    path('questionario/modulos/<str:nomeModulo>/', ModuloView.as_view(), name='obter_modulo'),
    path('questionario/', QuestionarioView.as_view(), name='obter-questionario'),
    path('modulos/<str:nomeModulo>/respostas/', SalvarRespostasModuloView.as_view(), name='salvar_respostas_modulo'),
    path('questionario/salvar-incompleta/', SalvarRespostaIncompletaView.as_view(), name='salvar_resposta_incompleta'),
    path('modulos/<str:identificador>/relatorio/', GerarRelatorioModuloView.as_view(), name='modulo-relatorio.pdf'),
    path('relatorios/', SearchRelatorio.as_view(), name='relatorios'),
    path('questionario/<str:identificador>/check_deadline/', CheckDeadlineResponde.as_view(), name='check-deadline'),
    path('relatorios/datas/', SearchAllDatesRelatorio.as_view(), name='all-dates-relatorios'),
    path('relatorios/dimensoes/', SearchLastDimensaoResultados.as_view(), name='all-dimensoes'),
    path('relatorio/modulo/', RespostaModuloViewSet.as_view(), name='relatorio-modulo'),
]