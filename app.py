import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from scipy import signal
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

    #A partir do tipo de processo retorna o tempo de execução e espera
    if(tipo_processo == '1'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
        
        #Isso ainda não funciona
        tempo_execucao = 0
        tempo_espera = 0
        tempo_total = 0

        for dado in dados_dict:
            tempo_total += dado['tempoExecucao']
            tempo_execucao += (tempo_total - dado['tempoChegada'])
            tempo_espera += (tempo_total - dado['tempoChegada'])

    elif(tipo_processo == '2'):
        return

        
    

if __name__ == '__main__':
    app.run()