from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ParametrosForm
from .utils import gerar_tabela_dados, exportar_para_xlsx
import pandas as pd
from datetime import datetime
from core.models import AppPermission

def has_pocos_permission(user, required_role='viewer'):
    """Check if user has permission to access pocos app with specified role."""
    if user.is_superuser:
        return True
    
    role_levels = {
        'viewer': 0,
        'editor': 1,
        'manager': 2,
        'admin': 3
    }
    
    required_level = role_levels.get(required_role, 0)
    
    try:
        permission = AppPermission.objects.get(user=user, app='pocos_app')
        user_level = role_levels.get(permission.role, 0)
        return user_level >= required_level
    except AppPermission.DoesNotExist:
        return False

@login_required
def index(request):
    """
    View para a página inicial com o formulário de parâmetros.
    """
    # Verificar permissão
    if not has_pocos_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Monitoramento de Poços de Água.")
        return redirect('dashboard:index')
    
    # Inicializar o formulário com o ano atual
    initial_data = {'ano': datetime.now().year}
    form = ParametrosForm(initial=initial_data)
    return render(request, 'pocos_app/index.html', {'form': form})

@login_required
def gerar_tabela(request):
    """
    View para processar o formulário e gerar a tabela de dados.
    """
    # Verificar permissão
    if not has_pocos_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para gerar relatórios no aplicativo de Monitoramento de Poços de Água.")
        return redirect('pocos_app:index')
    
    if request.method == 'POST':
        form = ParametrosForm(request.POST)
        if form.is_valid():
            # Armazenar os dados do formulário na sessão
            request.session['parametros'] = form.cleaned_data
            
            # Gerar a tabela de dados
            df = gerar_tabela_dados(form.cleaned_data)
            
            # Armazenar a tabela na sessão (convertendo para dicionário)
            request.session['tabela'] = df.to_dict('records')
            
            # Renderizar a página de resultados
            return render(request, 'pocos_app/resultados.html', {
                'tabela': df.to_html(classes='table table-striped', index=False),
                'form': form,
                'ano': form.cleaned_data['ano']
            })
    else:
        # Se não for POST, redirecionar para a página inicial
        return redirect('pocos_app:index')
    
    # Se o formulário não for válido, voltar para a página inicial com o formulário
    return render(request, 'pocos_app/index.html', {'form': form})

@login_required
def exportar_xlsx(request):
    """
    View para exportar a tabela para XLSX.
    """
    # Verificar permissão
    if not has_pocos_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para exportar relatórios no aplicativo de Monitoramento de Poços de Água.")
        return redirect('pocos_app:index')
    
    # Verificar se há dados na sessão
    if 'tabela' not in request.session:
        messages.error(request, "Nenhuma tabela foi gerada para exportação.")
        return redirect('pocos_app:index')
    
    # Recuperar a tabela da sessão
    tabela = request.session['tabela']
    df = pd.DataFrame(tabela)
    
    # Recuperar o ano do relatório da sessão
    ano = request.session.get('parametros', {}).get('ano', datetime.now().year)
    
    # Exportar para XLSX
    xlsx_data = exportar_para_xlsx(df)
    
    # Criar a resposta HTTP com o arquivo XLSX
    response = HttpResponse(
        xlsx_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=dados_poco_{ano}.xlsx'
    
    return response
