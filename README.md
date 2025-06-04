# Projeto Diagnóstico

O objetivo do Sistema de Diagnóstico é fornecer uma análise da empresa, permitindo que ela identifique áreas de melhoria e oportunidades de desenvolvimento através dos cursos oferecidos em parceria com o Hub de Inovação Fronteira da UEM. 

O sistema visa facilitar o processo de coleta de dados e geração de relatórios a fim de apoiar a tomada de decisão estratégica.

## Tecnologias Utilizadas
- Python
- Django
- Django REST Framework
- MySQL

## Funcionalidades
- API RESTful para gerenciamento de usuários, questionários e respostas.
- Autenticação JWT personalizada.
- Suporte a múltiplos tipos de questionários.
- Geração de relatórios empresariais.

## Como Executar o Projeto

### Pré-requisitos
- Python (3.12.3)
- MySQL

### Passos
1. Clone o repositório:
   ```bash
   git clone https://github.com/Yoshifg/projeto_diagnostico_api.git
   ```
   
2. Navegue até o diretório do projeto:
   ```bash
   cd projeto_diagnostico_api
   ```

3. Crie um .env.local e adicione:
   ```dotenv
   SECRET_KEY='django-key'
   DEBUG='True'

   # Domain Settings
   DOMAIN='domínio do frontend, sem protocolo ou porta'

   # Database Configuration
   DB_ENGINE='django.db.backends.mysql'
   DB_NAME='nome-bd'
   DB_USER='user-bd'
   DB_PASSWORD='senha-bd'
   DB_HOST='host-bd'
   DB_PORT='porta-bd'
   DB_INIT_COMMAND=SET sql_mode='STRICT_TRANS_TABLES'

   # Email Configuration
   EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST='serviço email'
   EMAIL_PORT='porta'
   EMAIL_USE_TLS='True'
   EMAIL_HOST_USER='email@email.com'
   EMAIL_HOST_PASSWORD='senha-email'

   # CORS Settings
   CORS_ALLOWED_ORIGINS='domínios que podem consumir a API via JavaScript, coloque o protocolo e a porta'

   # Security Settings
   AUTH_COOKIE_SECURE='False'
   ```

4. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   
5. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure o banco de dados no arquivo .env.local e aplique as migrações:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
7. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```