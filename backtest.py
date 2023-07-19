import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import backtesting as bt

# Contrato ZS=?
STOCK = "ZS=F"

# Crie um objeto ticker com o símbolo da ação desejada
ticker = yf.Ticker(STOCK)

historical_data = ticker.history(period="5y")


# Definir os parâmetros desejados
window = 14 # Janela em Dias
k_smoothing_window = 4 # fator de amortecimento de K
d_smoothing_window = 7 # fator de amortecimento de D


# ta.momentum.stoch(high, low, close, window=14, smooth_window=3, fillna=False)
K  = ta.momentum.stoch(historical_data['High'], historical_data['Low'], historical_data['Close'], window, k_smoothing_window)

# ta.momentum.stoch_signal(high, low, close, window=14, smooth_window=3, fillna=False)
D = ta.momentum.stoch_signal(historical_data['High'], historical_data['Low'], historical_data['Close'], window, d_smoothing_window)

# Atribuir os valores calculados ao DataFrame
historical_data['%K'] = K
historical_data['%D'] = D
# Criar uma coluna para registrar os sinais de compra e venda
historical_data['Sinal'] = None



def plotar_grafico(K, D, levelBuy, levelSell):
    plt.figure(figsize=(12, 6))

    # Plotar %K e %D com marcadores e linhas mais espessas
    plt.plot(K, label='%K', marker='o', linewidth=2)
    plt.plot(D, label='%D', marker='o', linewidth=2)

    # Plotar levelBuy e levelSell
    plt.axhline(y=levelBuy, color='green', linestyle='--', label='Level Buy')
    plt.axhline(y=levelSell, color='red', linestyle='--', label='Level Sell')

    # Configurar título, rótulos dos eixos e legenda
    plt.title('Stochastic Oscillator')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()

    # Exibir o gráfico
    plt.show()


# plotar_grafico(historical_data['%K'],historical_data['%D'],20,80)

def plotar_grafico_completo(K, D, levelBuy, levelSell, close, signal,Name, exclude_first=False):
     # Configurar tamanho do gráfico
    plt.figure(figsize=(30, 8))

    # Excluir os 20 primeiros valores, se necessário
    if exclude_first:
        K = K[20:]
        D = D[20:]
        close = close[20:]
        signal = signal[20:]

    # Criar subplots para os dois gráficos
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2, sharex=ax1)

    # Gráfico de Preços (Close)
    ax1.plot(close, label='Close', linestyle='-', linewidth=2)
    for i in range(0, len(signal)):
        if signal[i] == 'BUY':
            ax1.plot(signal.index[i], close[i], marker='^', markersize=10, color='green')
            ax1.text(signal.index[i], close[i], f'{close[i]:.2f}', ha='center', va='bottom', color='black')
        elif signal[i] == 'SELL':
            ax1.plot(signal.index[i], close[i], marker='v', markersize=10, color='red')
            ax1.text(signal.index[i], close[i], f'{close[i]:.2f}', ha='center', va='top', color='black')
    ax1.set_ylabel('Preço')

    # Gráfico dos Indicadores Estocásticos (%K e %D)
    ax2.plot(K, label='%K', marker='.', linewidth=1)
    ax2.plot(D, label='%D', marker='.', linewidth=1)
    # ax2.plot(K, label='%K',linewidth=1)
    # ax2.plot(D, label='%D',linewidth=1)
    for i in range(0, len(signal)):
        if signal[i] == 'BUY':
            ax2.plot(signal.index[i], K[i], marker='^', markersize=10, color='green')
        elif signal[i] == 'SELL':
            ax2.plot(signal.index[i], K[i], marker='v', markersize=10, color='red')
    ax2.axhline(y=levelBuy, color='green', linestyle='--', label='Level Buy')
    ax2.axhline(y=levelSell, color='red', linestyle='--', label='Level Sell')
    ax2.set_xlabel('Data')
    ax2.set_ylabel('Valor')

    # Configurar título e legenda
    ax1.set_title('Histórico de Preços e Indicadores Estocásticos'+"-"+Name)
    ax1.legend()
    ax2.legend()

    # Ajustar espaçamento entre os subplots
    plt.subplots_adjust(hspace=0.3)

    # Exibir o gráfico
    plt.show()


# Dados fictícios para demonstração
data = {
    '%K': [90, 67, 84, 76, 70, 45, 18, 32, 67, 85],
    '%D': [75, 78, 70, 56, 60, 33, 38, 39, 50, 80]
}

def definePontosV2(arrayK, arrayD, B=20, S=80,W = 1):
    win = W-1
    levelBuy = B
    levelSell = S
    crossOver = False
    crossUnder = True
    crossOver_entry = 0
    crossUnder_entry = 0
    estadoAtual = 'INIT'
    signals = []
    signals.append(estadoAtual)
    # print("Dia", 0, "- K =", arrayK[0], "D =", arrayD[0])
    for i in range(1, len(arrayK)):
        if arrayK[i-1] > arrayD[i-1] and arrayK[i] < arrayD[i]:
            crossOver = True
            crossUnder = False
            crossOver_entry = i
        if arrayK[i-1] < arrayD[i-1] and arrayK[i] > arrayD[i]:
            crossUnder = True
            crossOver = False
            crossUnder_entry = i

        buy = levelBuy > arrayK[i] and crossOver and estadoAtual != "BUY" and (i - crossOver_entry) <= win
        sell = arrayK[i] > levelSell and crossUnder and estadoAtual != "SELL" and estadoAtual != "INIT" and (i - crossUnder_entry) <= win

        if sell:
            signals.append("SELL")
            estadoAtual = "SELL"
            # print(i - crossUnder_entry)
        elif buy:
            signals.append("BUY")
            estadoAtual = "BUY"
            # print(i - crossOver_entry)
        else:
            signals.append("HOLD")
    return signals


historical_data['Sinal'] = definePontosV2(historical_data['%K'],historical_data['%D'],16,84,1)


historical_data.to_csv('soja.csv', index=True)



# Ler o arquivo CSV e carregar os dados em um DataFrame
df = pd.read_csv('soja.csv')


# Definir o valor inicial de caixa
caixa_inicial = 100000

# Inicializar variáveis para acompanhar a posição e o saldo da carteira
posicao = None
saldo_carteira = caixa_inicial

# Percorrer os dados do DataFrame
for index, row in df.iterrows():
    # print(saldo_carteira)
    if row['Sinal'] == 'BUY':
        if posicao is None:
            # Comprar ação
            quantidade_acoes_compradas = saldo_carteira // row['Close']
            posicao = quantidade_acoes_compradas * row['Close']
            saldo_carteira -= posicao
            print("Data da Compra :" +row["Date"])
            print(f"Compra: {quantidade_acoes_compradas} ações a {row['Close']} cada")
        else:
            print("Erro: posição já está ocupada")
    elif row['Sinal'] == 'SELL':
        if posicao is not None:
            # Vender ação
            print("Data da Venda :" +row["Date"])
            saldo_carteira += row['Close'] * quantidade_acoes_compradas
            lucro = (row['Close'] - (posicao / quantidade_acoes_compradas)) * quantidade_acoes_compradas
            print(f"Venda: {quantidade_acoes_compradas} ações a {row['Close']} cada (Lucro/Perda: {lucro})")
            posicao = None
            
        else:
            print("Erro: não há posição para vender")

# Calcular a variação percentual
variacao_percentual = (saldo_carteira - caixa_inicial) / caixa_inicial * 100

# Exibir o saldo final da carteira e a variação percentual
print(f"Saldo final da carteira: {saldo_carteira}")
print(f"Variação percentual: {variacao_percentual:.2f}%")

