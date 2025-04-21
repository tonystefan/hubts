import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import io

def gerar_datas_aleatorias(ano, dias_por_mes):
    """
    Gera datas aleatórias distribuídas conforme os dias por mês especificados.
    
    Args:
        ano: Ano do relatório
        dias_por_mes: Dicionário com a quantidade de dias para cada mês
        
    Returns:
        Lista de datas ordenadas
    """
    datas = []
    
    # Converter códigos de mês para números
    meses_map = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }
    
    # Para cada mês
    for codigo_mes, num_mes in meses_map.items():
        # Pular se não houver dias para este mês
        if dias_por_mes.get(f'dias_{codigo_mes}', 0) <= 0:
            continue
            
        # Obter o número de dias no mês
        dias_no_mes = calendar.monthrange(ano, num_mes)[1]
        
        # Número de dias a selecionar para este mês
        dias_a_selecionar = min(dias_por_mes.get(f'dias_{codigo_mes}', 0), dias_no_mes)
        
        # Selecionar dias aleatórios
        dias_selecionados = sorted(random.sample(range(1, dias_no_mes + 1), dias_a_selecionar))
        
        # Adicionar datas à lista
        for dia in dias_selecionados:
            datas.append(datetime(ano, num_mes, dia).strftime('%d/%m/%Y'))
    
    # Ordenar datas
    datas.sort(key=lambda x: datetime.strptime(x, '%d/%m/%Y'))
    
    return datas

def distribuir_valores(total, num_valores, max_valor):
    """
    Distribui um valor total em um número específico de valores aleatórios,
    respeitando um valor máximo por item.
    
    Args:
        total: Valor total a ser distribuído
        num_valores: Número de valores a gerar
        max_valor: Valor máximo por item
        
    Returns:
        Lista de valores que somam o total
    """
    if num_valores <= 0:
        return []
        
    if max_valor * num_valores < total:
        raise ValueError(f"Impossível distribuir {total} em {num_valores} valores com máximo de {max_valor} por valor")
    
    # Inicializar com valores mínimos
    min_valor = total / (num_valores * 10)  # Valor mínimo para evitar zeros
    valores = [min_valor] * num_valores
    restante = total - sum(valores)
    
    # Distribuir o restante aleatoriamente
    for _ in range(1000):  # Limite de iterações para evitar loop infinito
        if restante <= 0.0001:  # Tolerância para erros de ponto flutuante
            break
            
        # Escolher um índice aleatório
        idx = random.randint(0, num_valores - 1)
        
        # Calcular quanto podemos adicionar a este valor
        adicionar = min(random.uniform(0, restante), max_valor - valores[idx])
        
        # Adicionar ao valor e subtrair do restante
        valores[idx] += adicionar
        restante -= adicionar
    
    # Ajustar o último valor para garantir a soma exata
    if restante > 0:
        idx_menor = valores.index(min(valores))
        if valores[idx_menor] + restante <= max_valor:
            valores[idx_menor] += restante
        else:
            # Distribuir o restante entre todos os valores
            for i in range(num_valores):
                if valores[i] + (restante / num_valores) <= max_valor:
                    valores[i] += (restante / num_valores)
                    restante -= (restante / num_valores)
    
    # Arredondar para 3 casas decimais
    valores = [round(v, 3) for v in valores]
    
    # Ajuste final para garantir a soma exata
    diferenca = total - sum(valores)
    if abs(diferenca) > 0.001:
        idx = random.randint(0, num_valores - 1)
        valores[idx] = round(valores[idx] + diferenca, 3)
    
    return valores

def gerar_tabela_dados(parametros):
    """
    Gera a tabela de dados com base nos parâmetros fornecidos.
    
    Args:
        parametros: Dicionário com os parâmetros do formulário
        
    Returns:
        DataFrame pandas com os dados gerados
    """
    # Extrair parâmetros
    ano = parametros['ano']
    horimetro_inicial = parametros['horimetro_inicial']
    horimetro_final = parametros['horimetro_final']
    hidrometro_inicial = parametros['hidrometro_inicial']
    hidrometro_final = parametros['hidrometro_final']
    max_horimetro_diario = parametros['max_horimetro_diario']
    max_hidrometro_diario = parametros['max_hidrometro_diario']
    
    # Gerar datas aleatórias
    datas = gerar_datas_aleatorias(ano, parametros)
    
    # Calcular diferenças totais
    diferenca_horimetro = horimetro_final - horimetro_inicial
    diferenca_hidrometro = hidrometro_final - hidrometro_inicial
    
    # Distribuir valores de horímetro e hidrômetro
    valores_horimetro = distribuir_valores(diferenca_horimetro, len(datas), max_horimetro_diario)
    valores_hidrometro = distribuir_valores(diferenca_hidrometro, len(datas), max_hidrometro_diario)
    
    # Criar valores acumulados
    horimetro_acumulado = [horimetro_inicial]
    hidrometro_acumulado = [hidrometro_inicial]
    
    for i in range(len(valores_horimetro)):
        horimetro_acumulado.append(horimetro_acumulado[-1] + valores_horimetro[i])
        hidrometro_acumulado.append(hidrometro_acumulado[-1] + valores_hidrometro[i])
    
    # Remover o valor inicial (que era apenas para cálculo)
    horimetro_acumulado = horimetro_acumulado[1:]
    hidrometro_acumulado = hidrometro_acumulado[1:]
    
    # Arredondar para 3 casas decimais
    horimetro_acumulado = [round(v, 3) for v in horimetro_acumulado]
    hidrometro_acumulado = [round(v, 3) for v in hidrometro_acumulado]
    
    # Extrair códigos de mês das datas
    meses = [datetime.strptime(data, '%d/%m/%Y').strftime('%b').lower() for data in datas]
    
    # Obter vazões e horas/dia para cada data com base no mês
    vazoes = []
    horas_dia = []
    
    for mes in meses:
        # Converter abreviação em português para código
        mes_codigo = {
            'jan': 'jan', 'fev': 'fev', 'mar': 'mar', 'abr': 'abr', 
            'mai': 'mai', 'jun': 'jun', 'jul': 'jul', 'ago': 'ago', 
            'set': 'set', 'out': 'out', 'nov': 'nov', 'dez': 'dez'
        }.get(mes, 'jan')  # Default para janeiro se não encontrar
        
        vazoes.append(parametros.get(f'vazao_{mes_codigo}', 0.03))
        horas_dia.append(parametros.get(f'horas_{mes_codigo}', 0.40))
    
    # Criar DataFrame
    df = pd.DataFrame({
        'Data': datas,
        'Horímetro': horimetro_acumulado,
        'Hidrômetro': hidrometro_acumulado,
        'Vazão m³': [round(random.uniform(0.55, 0.60), 2) for _ in range(len(datas))],
        'Vazão m³/h': vazoes,
        'Horas/Dia': horas_dia
    })
    
    return df

def exportar_para_xlsx(df):
    """
    Exporta o DataFrame para um arquivo XLSX em memória.
    
    Args:
        df: DataFrame pandas com os dados
        
    Returns:
        Bytes do arquivo XLSX
    """
    output = io.BytesIO()
    
    # Criar um escritor Excel
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Escrever o DataFrame para o Excel
    df.to_excel(writer, sheet_name='Dados', index=False)
    
    # Salvar o arquivo
    writer.close()
    
    # Retornar os bytes
    output.seek(0)
    return output.getvalue()
