import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from collections import defaultdict
import base64
import json
import queue

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

    #Criação de dicionário para armazenar os processos em execução para o gráfico
    grupos_grafico = defaultdict(list)

    #Criação de fila para armazenar os processos e variaveis adicionais
    fila = queue.Queue()
    incrementador = 0
    dado_em_processamento = defaultdict(list)

    #Criação de listas e dicionarios para armazenar os tempos de execução e espera
    tempos_execucao = defaultdict(list)
    tempos_espera = defaultdict(list)
    lista_valores_execucao = []
    lista_valores_espera = []


    #A partir do tipo de processo retorna o tempo de execução e espera
    if(tipo_processo == '1'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
        
        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)

            dado_em_processamento, incrementador = processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict)

            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break

    elif(tipo_processo == '2'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
    
        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)

            #DIFERENTE AQUI!!!!
            #Reordena a fila atual pelo tempo de execução dos processos ainda não iniciados. NÃO É EFICIENTE
            itens = []
            while not fila.empty():
                itens.append(fila.get())
            itens.sort(key=lambda x: int(x['tempoServico']))
            for item in itens:
                fila.put(item)

            #FIM DA DIFERENÇA
                
            dado_em_processamento, incrementador = processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict)

            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break

    elif(tipo_processo == '3'):
        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])

        #Variavel que garante que cada processo tenha no máximo 2 segundos de processamento
        tempo_processamento = 0

        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)
            
            #Se não houver processo em execução, pega o próximo da fila
            if(not dado_em_processamento):
                dado_em_processamento = fila.get()
                dado_em_processamento['tempoInicioProcessoAtual'] = x

            #Se o tempo de execução do processo atual for 0, adiciona o tempo de finalização do processo atual, salva no dicionario de gráficos e pega o próximo da fila
            if(int(dado_em_processamento['tempoRestante']) == 0):
                dado_em_processamento['tempoFinalProcessoAtual'] = x
                grupos_grafico[dado_em_processamento['nome']].append((dado_em_processamento['tempoInicioProcessoAtual'], (dado_em_processamento['tempoFinalProcessoAtual'] - dado_em_processamento['tempoInicioProcessoAtual']), int(dado_em_processamento['tempoChegada'])))
                
                adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento)

                incrementador += 1

                #DIFERENÇA AQUI PARA ESSE ALGORITMO!!!!
                #Zera o tempo de processamento para que o próximo processo possa ser executado
                tempo_processamento = 0

                #FIM DA DIFERENÇA

                #Se a fila não estiver vazia, pega o próximo da fila
                if(not fila.empty()):
                    dado_em_processamento = fila.get()
                    dado_em_processamento['tempoInicioProcessoAtual'] = x


            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                
                #DIFERENTE AQUI PARA ESSE ALGORITMO!!!!
                #Se tiver mais algum processo na fila com tempo restante menor que o processo atual, coloca o processo atual no final da fila e pega o próximo da fila
                if(not fila.empty()):
                    if(tempo_processamento == 2):
                        dado_em_processamento['tempoFinalProcessoAtual'] = x
                        grupos_grafico[dado_em_processamento['nome']].append((dado_em_processamento['tempoInicioProcessoAtual'], (dado_em_processamento['tempoFinalProcessoAtual'] - dado_em_processamento['tempoInicioProcessoAtual']), int(dado_em_processamento['tempoChegada'])))
                        
                        adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento)

                        fila.put(dado_em_processamento)
                        dado_em_processamento = fila.get()
                        dado_em_processamento['tempoInicioProcessoAtual'] = x
                        tempo_processamento = 0
                #FIM DA DIFERENÇA
                
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1
                tempo_processamento += 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break

    
    elif(tipo_processo == '4'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
    
        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)

            #DIFERENTE AQUI PARA ESSE ALGORITMO!!!!
            #Reordena a fila atual pelo tempo de execução de todos os processos. NÃO É EFICIENTE
            itens = []
            while not fila.empty():
                itens.append(fila.get())
            itens.sort(key=lambda x: int(x['tempoRestante']))
            for item in itens:
                fila.put(item)

            #FIM DA DIFERENÇA
            
            dado_em_processamento, incrementador = processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict)

            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                
                #DIFERENTE AQUI PARA ESSE ALGORITMO!!!!
                #Se tiver mais algum processo na fila com tempo restante menor que o processo atual, coloca o processo atual no final da fila e pega o próximo da fila
                if(not fila.empty()):
                    if(int(fila.queue[0]['tempoRestante']) < int(dado_em_processamento['tempoRestante'])):
                        dado_em_processamento['tempoFinalProcessoAtual'] = x
                        grupos_grafico[dado_em_processamento['nome']].append((dado_em_processamento['tempoInicioProcessoAtual'], (dado_em_processamento['tempoFinalProcessoAtual'] - dado_em_processamento['tempoInicioProcessoAtual']), int(dado_em_processamento['tempoChegada'])))
                        
                        adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento)

                        fila.put(dado_em_processamento)
                        dado_em_processamento = fila.get()
                        dado_em_processamento['tempoInicioProcessoAtual'] = x
                #FIM DA DIFERENÇA
                
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break

    elif(tipo_processo == '5'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
    
        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)

            #DIFERENTE AQUI!!!!
            #Reordena a fila atual pela prioridade dos processos ainda não iniciados. NÃO É EFICIENTE
            itens = []
            while not fila.empty():
                itens.append(fila.get())
            itens.sort(key=lambda x: int(x['prioridade']), reverse=True)
            for item in itens:
                fila.put(item)

            #FIM DA DIFERENÇA
                
            dado_em_processamento, incrementador = processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict)

            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break

    elif(tipo_processo == '6'):

        #Ordena os processos por tempo de chegada
        dados_dict.sort(key=lambda x: x['tempoChegada'])
    
        for x in range(0,1000,1):
            
            adiciona_processo_fila(dados_dict, fila, x)
            
            #DIFERENTE AQUI PARA ESSE ALGORITMO!!!!
            #Reordena a fila atual pela prioridade dos processos. NÃO É EFICIENTE
            itens = []
            while not fila.empty():
                itens.append(fila.get())
            itens.sort(key=lambda x: int(x['prioridade']), reverse=True)
            for item in itens:
                fila.put(item)

            #FIM DA DIFERENÇA
                
            dado_em_processamento, incrementador = processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict)
            
            #Se o tempo de execução do processo atual for maior que 0, decrementa o tempo de execução em 1
            if(int(dado_em_processamento['tempoRestante']) > 0):
                #DIFERENTE AQUI PARA ESSE ALGORITMO!!!!
                #Se tiver mais algum processo na fila com tempo restante menor que o processo atual, coloca o processo atual no final da fila e pega o próximo da fila
                if(not fila.empty()):
                    if(int(fila.queue[0]['prioridade']) > int(dado_em_processamento['prioridade'])):
                        dado_em_processamento['tempoFinalProcessoAtual'] = x
                        grupos_grafico[dado_em_processamento['nome']].append((dado_em_processamento['tempoInicioProcessoAtual'], (dado_em_processamento['tempoFinalProcessoAtual'] - dado_em_processamento['tempoInicioProcessoAtual']), int(dado_em_processamento['tempoChegada'])))
                        
                        adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento)

                        fila.put(dado_em_processamento)
                        dado_em_processamento = fila.get()
                        dado_em_processamento['tempoInicioProcessoAtual'] = x
                #FIM DA DIFERENÇA
                
                dado_em_processamento['tempoRestante'] = int(dado_em_processamento['tempoRestante']) - 1

            #Se a fila estiver vazia e o incrementador for maior que o tamanho do dicionário de dados, para o loop
            if(fila.empty() and incrementador >= len(dados_dict)):
                break


    #Reordena tempos_execucao para que os processos sejam desenhados na ordem correta
    tempos_execucao = {k: tempos_execucao[k] for k in sorted(tempos_execucao, key=lambda x: int(x[1:]))}

    # Cria um novo dicionário com o último valor para cada chave
    ultimo_valor_tempos_execucao = {k: v[-1] for k, v in tempos_execucao.items()}

    #Converte os valores de tempos_execucao para listas
    lista_valores_execucao = list(ultimo_valor_tempos_execucao.values())

    #Reordena tempos_espera para que os processos sejam desenhados na ordem correta
    tempos_espera = {k: tempos_espera[k] for k in sorted(tempos_espera, key=lambda x: int(x[1:]))}

    # Cria um novo dicionário com o último valor para cada chave
    ultimo_valor_tempos_espera = {k: v[-1] for k, v in tempos_espera.items()}
    
    #Converte os valores de tempos_espera para listas
    lista_valores_espera = list(ultimo_valor_tempos_espera.values())


    encoded_image = desenha_grafico(grupos_grafico)

    return jsonify({'temposServico': lista_valores_execucao, 'temposEspera': lista_valores_espera, 'tempoExecucaoFinal': sum(lista_valores_execucao) / len(lista_valores_execucao), 'tempoEsperaFinal': sum(lista_valores_espera) / len(lista_valores_espera), 'grafico': f'<img src="data:image/png;base64,{encoded_image}">'})        




def processamento_inicial(x, fila, dado_em_processamento, grupos_grafico, tempos_execucao, tempos_espera, incrementador, dados_dict):
    #Se não houver processo em execução, pega o próximo da fila
    if(not dado_em_processamento):
        dado_em_processamento = fila.get()
        dado_em_processamento['tempoInicioProcessoAtual'] = x

    #Se o tempo de execução do processo atual for 0, adiciona o tempo de finalização do processo atual, salva no dicionario de gráficos e pega o próximo da fila
    if(int(dado_em_processamento['tempoRestante']) == 0):
        dado_em_processamento['tempoFinalProcessoAtual'] = x
        grupos_grafico[dado_em_processamento['nome']].append((dado_em_processamento['tempoInicioProcessoAtual'], (dado_em_processamento['tempoFinalProcessoAtual'] - dado_em_processamento['tempoInicioProcessoAtual']), int(dado_em_processamento['tempoChegada'])))
                
        adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento)

        incrementador += 1

        #Se a fila não estiver vazia, pega o próximo da fila
        if(not fila.empty()):
            dado_em_processamento = fila.get()
            dado_em_processamento['tempoInicioProcessoAtual'] = x

    
    return dado_em_processamento, incrementador




def adiciona_valor_expressao_algebrica(tempos_execucao, tempos_espera, dado_em_processamento):
    #Adiciona valores nas listas para gerar as expressões algébricas
    tempos_execucao[dado_em_processamento['nome']].append(dado_em_processamento['tempoFinalProcessoAtual'] - int(dado_em_processamento['tempoChegada']))
    tempos_espera[dado_em_processamento['nome']].append(dado_em_processamento['tempoFinalProcessoAtual'] - int(dado_em_processamento['tempoChegada']) - int(dado_em_processamento['tempoServico']))
    



def adiciona_processo_fila(dados_dict, fila, x):
    #Expressão que encontra todos os processos que iniciam no tempo x.
    processos_encontrados = list(filter(lambda p: int(p['tempoChegada']) == x, dados_dict))
            
    #Coloca todos os processos que iniciam no tempo x na fila
    for processo in processos_encontrados:
        processo['tempoRestante'] = processo['tempoServico']
        processo['tempoInicioProcessoAtual'] = 0
        processo['tempoFinalProcessoAtual'] = 0
        fila.put(processo)





def desenha_grafico(grupos_grafico):

    #Calcula o valor máximo para o eixo x do gráfico
    valor_maximo = max(valor[0] + valor[1] for valores in grupos_grafico.values() for valor in valores)

    #Reordena grupos_grafico para que os processos sejam desenhados na ordem correta
    grupos_grafico = {k: grupos_grafico[k] for k in sorted(grupos_grafico, key=lambda x: int(x[1:]))}

    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()
        
    # Setting Y-axis limits
    gnt.set_ylim(0, (len(grupos_grafico.keys()) * 10 + 10))
        
    # Setting X-axis limits
    gnt.set_xlim(0, valor_maximo)
        
    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Tempo processamento')
    gnt.set_ylabel('Processos')
        
    # Setting ticks on y-axis
    gnt.set_yticks(np.arange(10, (len(grupos_grafico.keys()) * 10 + 10), 10))
    # Labelling tickes of y-axis
    gnt.set_yticklabels(grupos_grafico.keys())
        
    # Setting graph attribute
    gnt.grid(True)
    
    #Representa o tamanha de cada coluna. Meramente visual
    numero_processo_atual = 6

    for nome_processo, valores in grupos_grafico.items():

        # Crie a  barra de espera do processo
        gnt.broken_barh([(valores[0][2], (valores[-1][0] - valores[0][2]))], (numero_processo_atual, 8), facecolors='bisque')
        
        #Cria as barras de execução do processo
        for valor in valores:
            gnt.broken_barh([(valor[0], valor[1])], (numero_processo_atual, 8), facecolors='tab:orange')
            
        numero_processo_atual += 10
        

    # Criação do objeto FigureCanvas e renderização do gráfico
    canvas = FigureCanvas(fig)
    buffer = BytesIO()
    canvas.print_png(buffer)
    image_data = buffer.getvalue()

    # Codificação da imagem em base64
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    return encoded_image




if __name__ == '__main__':
    app.run()