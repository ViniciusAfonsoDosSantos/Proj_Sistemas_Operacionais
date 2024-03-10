import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from scipy import signal
from collections import defaultdict
import control
import base64
import json

app = Flask(__name__)


#Redireciona página principal.
@app.route('/')
def index():
    return render_template('index.html')

#Recebe AJAX do front-end
@app.route('/gerenciador-processos')
def gerencia_processos():
    #Representa o dado em formato JSON
    dados = request.args.get('processos', None)
    tipo_processo = request.args.get('opcaoSelecionada', None)
    dados_dict = json.loads(dados)

    #Criação de dicionário para armazenar os processos em execução
    grupos_execucao = defaultdict(list)
        
    #Variaveis que representam output
    tempos_execucao = []
    tempos_espera = []
    tempo_execucao_final = 0
    tempo_espera_final = 0
    tempo_atual = 0

    #A partir do tipo de processo retorna o tempo de execução e espera
    if(tipo_processo == '1'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])

        for dado in dados_dict:
            grupos_execucao[dado['nome']].append((tempo_atual, (tempo_atual + int(dado['tempoServico'])), int(dado['tempoChegada'])))
            tempos_execucao.append(int(dado['tempoServico']) + tempo_atual - int(dado['tempoChegada']))
            tempos_espera.append(tempo_atual - int(dado['tempoChegada']))
            tempo_atual = tempo_atual + int(dado['tempoServico'])
            
        tempo_execucao_final = sum(tempos_execucao) / len(tempos_execucao)
        tempo_espera_final = sum(tempos_espera) / len(tempos_espera)

    elif(tipo_processo == '2'):

        #Ordena os processos por tempo de execução
        dados_dict.sort(key=lambda x: x['tempoServico'])

        for dado in dados_dict:
            grupos_execucao[dado['nome']].append((tempo_atual, (tempo_atual + int(dado['tempoServico'])), int(dado['tempoChegada'])))
            tempos_execucao.append(int(dado['tempoServico']) + tempo_atual - int(dado['tempoChegada']))
            tempos_espera.append(tempo_atual - int(dado['tempoChegada']))
            tempo_atual = tempo_atual + int(dado['tempoServico'])
            
        tempo_execucao_final = sum(tempos_execucao) / len(tempos_execucao)
        tempo_espera_final = sum(tempos_espera) / len(tempos_espera)

    elif(tipo_processo == '3'):
        return

    valor_maximo = max(numero for valores in grupos_execucao.values() for valor in valores for numero in valor)

    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()
        
    # Setting Y-axis limits
    gnt.set_ylim(0, (len(grupos_execucao.keys()) * 10 + 10))
        
    # Setting X-axis limits
    gnt.set_xlim(0, valor_maximo)
        
    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Tempo processamento')
    gnt.set_ylabel('Processos')
        
    # Setting ticks on y-axis
    gnt.set_yticks(np.arange(10, (len(grupos_execucao.keys()) * 10 + 10), 10))
    # Labelling tickes of y-axis
    gnt.set_yticklabels(grupos_execucao.keys())
        
    # Setting graph attribute
    gnt.grid(True)
        
    numero_processo_atual = 6
        
    for nome_processo, valores in grupos_execucao.items():

        # Determina o tempo de inicio processamento, o último tempo de processamento, e o tempo de chegada do processo
        tempo_chegada_processamento = valores[0][0]
        ultimo_tempo_processamento = valores[-1][1]
        tempo_chegada_processo = valores[0][2]

        # Crie a nova barra
        gnt.broken_barh([(tempo_chegada_processo, ultimo_tempo_processamento - tempo_chegada_processo)], (numero_processo_atual, 8), facecolors='bisque')
        gnt.broken_barh([(tempo_chegada_processamento, ultimo_tempo_processamento - tempo_chegada_processamento)], (numero_processo_atual, 8), facecolors='tab:orange')
            
        numero_processo_atual += 10
        

    # Criação do objeto FigureCanvas e renderização do gráfico
    canvas = FigureCanvas(fig)
    buffer = BytesIO()
    canvas.print_png(buffer)
    image_data = buffer.getvalue()

    # Codificação da imagem em base64
    encoded_image = base64.b64encode(image_data).decode('utf-8')


    return jsonify({'temposServico': tempos_execucao, 'temposEspera': tempos_espera, 'tempoExecucaoFinal': tempo_execucao_final, 'tempoEsperaFinal': tempo_espera_final, 'grafico': f'<img src="data:image/png;base64,{encoded_image}">'})        

        
    

if __name__ == '__main__':
    app.run()