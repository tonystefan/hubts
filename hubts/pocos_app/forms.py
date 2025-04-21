from django import forms
from datetime import datetime
import calendar

class ParametrosForm(forms.Form):
    ano = forms.IntegerField(label='Ano do Relatório', min_value=2000, max_value=2100, 
                             initial=datetime.now().year)
    horimetro_inicial = forms.FloatField(label='Horímetro Inicial', min_value=0)
    horimetro_final = forms.FloatField(label='Horímetro Final', min_value=0)
    hidrometro_inicial = forms.FloatField(label='Hidrômetro Inicial', min_value=0)
    hidrometro_final = forms.FloatField(label='Hidrômetro Final', min_value=0)
    
    # Valores máximos diários
    max_horimetro_diario = forms.FloatField(label='Valor Máximo Diário do Horímetro', min_value=0.01)
    max_hidrometro_diario = forms.FloatField(label='Valor Máximo Diário do Hidrômetro', min_value=0.01)
    
    # Opção para calcular automaticamente vazão e horas/dia
    calcular_automaticamente = forms.BooleanField(
        label='Calcular automaticamente vazão m³/h e horas/dia com base nos valores de horímetro e hidrômetro',
        required=False,
        initial=False
    )
    
    # Opção para projetar até a data atual (apenas para o ano corrente)
    projetar_ate_hoje = forms.BooleanField(
        label='Projetar apenas até a data atual (apenas para o ano corrente)',
        required=False,
        initial=False
    )
    
    # Valores mensais
    MESES = [
        ('jan', 'Janeiro'),
        ('fev', 'Fevereiro'),
        ('mar', 'Março'),
        ('abr', 'Abril'),
        ('mai', 'Maio'),
        ('jun', 'Junho'),
        ('jul', 'Julho'),
        ('ago', 'Agosto'),
        ('set', 'Setembro'),
        ('out', 'Outubro'),
        ('nov', 'Novembro'),
        ('dez', 'Dezembro'),
    ]
    
    # Campos dinâmicos para cada mês
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obter o ano atual para verificar se estamos no ano corrente
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        dia_atual = datetime.now().day
        
        # Obter o ano do formulário, se disponível
        ano_form = None
        if args and isinstance(args[0], dict) and 'ano' in args[0]:
            ano_form = args[0]['ano']
        elif kwargs.get('initial') and 'ano' in kwargs['initial']:
            ano_form = kwargs['initial']['ano']
        else:
            ano_form = ano_atual
        
        # Verificar se é ano bissexto
        is_bissexto = calendar.isleap(ano_form)
        
        for i, (codigo, nome) in enumerate(self.MESES):
            mes_num = i + 1  # Janeiro = 1, Fevereiro = 2, etc.
            
            # Determinar o número máximo de dias para este mês
            if codigo == 'fev':
                max_dias = 29 if is_bissexto else 28
            elif codigo in ['abr', 'jun', 'set', 'nov']:
                max_dias = 30
            else:
                max_dias = 31
            
            # Para o ano atual, ajustar os dias máximos para meses futuros ou o mês atual
            dias_inicial = max_dias
            if ano_form == ano_atual:
                if mes_num > mes_atual:
                    # Mês futuro no ano atual - definir como 0 dias
                    dias_inicial = 0
                elif mes_num == mes_atual:
                    # Mês atual - definir como o dia atual
                    dias_inicial = dia_atual
            
            self.fields[f'vazao_{codigo}'] = forms.FloatField(
                label=f'Vazão m³/h ({nome})', 
                min_value=0,
                initial=0.03
            )
            self.fields[f'horas_{codigo}'] = forms.FloatField(
                label=f'Horas/Dia ({nome})', 
                min_value=0,
                initial=0.40
            )
            self.fields[f'dias_{codigo}'] = forms.IntegerField(
                label=f'Dias ({nome})', 
                min_value=0, 
                max_value=max_dias,
                initial=dias_inicial,
                help_text=f'Máximo: {max_dias} dias'
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que o horímetro final é maior que o inicial
        horimetro_inicial = cleaned_data.get('horimetro_inicial')
        horimetro_final = cleaned_data.get('horimetro_final')
        if horimetro_inicial and horimetro_final and horimetro_final <= horimetro_inicial:
            raise forms.ValidationError('O horímetro final deve ser maior que o inicial.')
        
        # Validar que o hidrômetro final é maior que o inicial
        hidrometro_inicial = cleaned_data.get('hidrometro_inicial')
        hidrometro_final = cleaned_data.get('hidrometro_final')
        if hidrometro_inicial and hidrometro_final and hidrometro_final <= hidrometro_inicial:
            raise forms.ValidationError('O hidrômetro final deve ser maior que o inicial.')
        
        # Se a opção de cálculo automático estiver marcada, calcular vazão e horas/dia
        if cleaned_data.get('calcular_automaticamente'):
            # Calcular a diferença total
            diferenca_horimetro = horimetro_final - horimetro_inicial
            diferenca_hidrometro = hidrometro_final - hidrometro_inicial
            
            # Contar o número total de dias
            total_dias = 0
            for codigo, _ in self.MESES:
                total_dias += cleaned_data.get(f'dias_{codigo}', 0)
            
            if total_dias > 0:
                # Calcular vazão média (m³/h)
                vazao_media = diferenca_hidrometro / diferenca_horimetro if diferenca_horimetro > 0 else 0
                
                # Calcular horas/dia média
                horas_dia_media = diferenca_horimetro / total_dias if total_dias > 0 else 0
                
                # Atualizar os valores nos campos
                for codigo, _ in self.MESES:
                    if cleaned_data.get(f'dias_{codigo}', 0) > 0:
                        cleaned_data[f'vazao_{codigo}'] = round(vazao_media, 3)
                        cleaned_data[f'horas_{codigo}'] = round(horas_dia_media, 3)
        
        # Se a opção de projetar até hoje estiver marcada e for o ano atual
        if cleaned_data.get('projetar_ate_hoje') and cleaned_data.get('ano') == datetime.now().year:
            mes_atual = datetime.now().month
            dia_atual = datetime.now().day
            
            # Ajustar os dias para meses futuros e o mês atual
            for i, (codigo, _) in enumerate(self.MESES):
                mes_num = i + 1  # Janeiro = 1, Fevereiro = 2, etc.
                
                if mes_num > mes_atual:
                    # Mês futuro - definir como 0 dias
                    cleaned_data[f'dias_{codigo}'] = 0
                elif mes_num == mes_atual:
                    # Mês atual - definir como o dia atual
                    cleaned_data[f'dias_{codigo}'] = min(cleaned_data.get(f'dias_{codigo}', 0), dia_atual)
        
        return cleaned_data
