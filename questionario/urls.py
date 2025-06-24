from django.urls import path
from .views import (
    QuestionarioView,
    SalvarRespostasModuloView,
    ModuloView,
    GerarRelatorioModuloView,
    SearchRelatorio
)

urlpatterns = [
    path('questionario/modulos/<str:nomeModulo>/', ModuloView.as_view(), name='obter_modulo'),
    path('questionario/', QuestionarioView.as_view(), name='obter-questionario'),
    path('modulos/<str:nomeModulo>/respostas/', SalvarRespostasModuloView.as_view(), name='salvar_respostas_modulo'),
    path('modulos/<str:identificador>/relatorio/', GerarRelatorioModuloView.as_view(), name='modulo-relatorio.pdf'),
    path('relatorios/', SearchRelatorio.as_view(), name='relatorios')
]