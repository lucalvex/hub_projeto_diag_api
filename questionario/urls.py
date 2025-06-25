from django.urls import path
from .views import (
    QuestionarioView,
    SalvarRespostasModuloView,
    ModuloView,
    GerarRelatorioModuloView,
    SearchRelatorio,
    CheckDeadlineResponde,
    SearchAllDatesRelatorio
)

urlpatterns = [
    path('questionario/modulos/<str:nomeModulo>/', ModuloView.as_view(), name='obter_modulo'),
    path('questionario/', QuestionarioView.as_view(), name='obter-questionario'),
    path('modulos/<str:nomeModulo>/respostas/', SalvarRespostasModuloView.as_view(), name='salvar_respostas_modulo'),
    path('modulos/<str:identificador>/relatorio/', GerarRelatorioModuloView.as_view(), name='modulo-relatorio.pdf'),
    path('relatorios/', SearchRelatorio.as_view(), name='relatorios'),
    path('questionario/<str:identificador>/check_deadline/', CheckDeadlineResponde.as_view(), name='check-deadline'),
    path('relatorios/datas/', SearchAllDatesRelatorio.as_view(), name='all-dates-relatorios'),
]