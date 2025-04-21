# Plataforma Multi-App com Django

Este arquivo README contém instruções para implantação da plataforma multi-app no Render com PostgreSQL.

## Visão Geral

A plataforma multi-app é uma aplicação Django que inclui:

1. **Sistema de Permissionamento**: Controle de acesso por usuário e por aplicativo
2. **Aplicativo de Poços de Água**: Sistema para análise de consumo de poços de bombeamento de água
3. **Aplicativo de Caronas**: Sistema para registro e contabilização de caronas para treinos de handball

## Requisitos

- Python 3.10.12
- PostgreSQL
- Todas as dependências listadas em requirements.txt

## Configuração para Implantação no Render

### 1. Criar um Banco de Dados PostgreSQL no Render

1. Faça login na sua conta do Render (https://render.com)
2. Navegue até "New +" e selecione "PostgreSQL"
3. Preencha os seguintes campos:
   - Name: multi-app-db (ou outro nome de sua preferência)
   - Database: multi_app_db
   - User: multi_app_user
   - Region: Escolha a região mais próxima de você
4. Clique em "Create Database"
5. Após a criação, anote a "Internal Database URL" que será usada na configuração do serviço web

### 2. Criar um Serviço Web no Render

1. Navegue até "New +" e selecione "Web Service"
2. Conecte seu repositório GitHub (você precisará fazer upload do código para um repositório GitHub)
3. Preencha os seguintes campos:
   - Name: multi-app-platform (ou outro nome de sua preferência)
   - Environment: Python
   - Region: Escolha a mesma região do banco de dados
4. Na seção "Build Command", insira: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Na seção "Start Command", insira: `gunicorn core_platform.wsgi:application`
6. Em "Advanced", adicione as seguintes variáveis de ambiente:
   - `DATABASE_URL`: Cole a "Internal Database URL" do seu banco de dados PostgreSQL
   - `SECRET_KEY`: Gere uma chave secreta aleatória (pode usar https://djecrety.ir/)
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: seu-app.onrender.com (substitua pelo domínio real do seu app)
7. Clique em "Create Web Service"

### 3. Migrar o Banco de Dados

Após a implantação inicial, você precisará executar as migrações do banco de dados:

1. No painel do seu serviço web no Render, vá para a aba "Shell"
2. Execute os seguintes comandos:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Siga as instruções para criar um superusuário (administrador)

## Uso da Plataforma

### Acesso ao Painel de Administração

1. Acesse `https://seu-app.onrender.com/admin/`
2. Faça login com as credenciais do superusuário criado anteriormente
3. No painel de administração, você pode:
   - Gerenciar usuários e suas permissões
   - Configurar os aplicativos
   - Gerenciar dados do sistema

### Aplicativo de Poços de Água

Acesse `https://seu-app.onrender.com/pocos/` para:
- Inserir parâmetros para análise de consumo de poços
- Gerar relatórios com distribuição de consumo de água
- Exportar dados para formato XLSX

### Aplicativo de Caronas

Acesse `https://seu-app.onrender.com/caronas/` para:
- Registrar rotas e participantes de caronas
- Calcular divisão de custos entre participantes
- Visualizar relatórios de débitos/créditos

## Manutenção e Suporte

Para atualizar a aplicação:
1. Faça as alterações no código
2. Atualize o repositório GitHub
3. O Render detectará automaticamente as alterações e implantará a nova versão

Para escalar a aplicação:
1. No painel do seu serviço web no Render, vá para a aba "Settings"
2. Ajuste os recursos (CPU/RAM) conforme necessário

## Solução de Problemas

Se encontrar problemas durante a implantação:
1. Verifique os logs no painel do Render
2. Certifique-se de que todas as variáveis de ambiente estão configuradas corretamente
3. Verifique se o banco de dados PostgreSQL está acessível
