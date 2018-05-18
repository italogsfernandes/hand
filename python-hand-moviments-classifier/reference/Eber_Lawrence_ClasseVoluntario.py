import numpy as np
import pandas as pd
import seaborn as sns
from scipy import signal
from sklearn.svm import SVC
from sklearn.base import clone
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score, cross_val_predict, cross_validate, StratifiedKFold

class SinalVoluntario():

    def __init__(self, nome):
        self.nome = nome

    def CarregaDados(self):
        lista = np.array(range(760000)) # Lista para servir de index para o DATAFRAME.
        L = []
        for i in range(2):
            for j in range(4):
                dados = pd.read_table(self.nome+str(i+1)+str(j+1)+'-Final.txt', sep=';', header=None)
                df = pd.DataFrame(0, index=lista, columns='CH1 CH2 CH3 CH4 Trigger'.split())
                df['CH1'], df['CH2'], df['CH3'], df['CH4'], df['Trigger'] = dados[0], dados[1], dados[2], dados[3], dados[4]
                L.append(df)
        return (L[0],L[1],L[2],L[3],L[4],L[5],L[6],L[7]) # Retorna um DATAFRAME com os dados do .txt

    def CarregaRespostas(self):
        '''
        Retorna um SERIES com a sequencia de movimentos armazenada em um .txt 
        Os movimentos são:
        1 -> Supinar
        2 -> Pronar
        3 -> Pinçar
        4 -> Fechar
        5 -> Estender
        6 -> Flexionar
        O SERIES retornado possui todas as respostas das 8 coletas - Total de 480 respostas [0, ..., 479]
        '''
        listaresposta = []
        for i in range(2):
            for j in range(4):
                resposta = np.array(pd.read_table(self.nome+str(i+1)+str(j+1)+'-Resposta.txt', header=None))
                for v in resposta:
                    if v == 1:
                        listaresposta.append('Supinar')
                    if v == 2:
                        listaresposta.append('Pronar')
                    if v == 3:
                        listaresposta.append('Pinçar')
                    if v == 4:
                        listaresposta.append('Fechar')
                    if v == 5:
                        listaresposta.append('Estender')
                    if v == 6:
                        listaresposta.append('Flexionar')
        TargetEMG = pd.DataFrame(0, index=range(0,480), columns=''.split())
        TargetEMG['Resposta'] = listaresposta
        return TargetEMG     


#
# Detalhes do sinal e parâmetros para a construção dos filtros
#
DelayT = 500 # Tempo de atraso no TRIGER para sincronização SINAL/TRIGGER em amostras
fs = 2000  # Frequência de amostragem (Hz)
Fnotch = 60.0  # Frequência para remoer com o filtro NOTCH - Remover interferência da rede
Fpa = 10.0 # Frequência de corte do filtro PASSA-ALTA - Remoção do Offset gerado pelo sinal DC
Fpb = 20.0 # Frequência de corte do filtro PASSA-BAIXA - Suavização do sinal
Q = 1  # Fator de qualidade do filtro NOTCH

# Frequência normalizada:
Wnotch = Fnotch/(fs/2) # Para o filtro NOTCH
Wpb = Fpb/(fs/2) # Para o filtro PASSA-BAIXA
Wpa = Fpa/(fs/2) # Para o filtro PASSA-ALTA


#
# Construção de filtros
#
b1, a1 = signal.iirnotch(Wnotch, Q) # Design notch filter - Fc = 60Hz
b2, a2 = signal.butter(2, Wpa, 'highpass') # Design butter filter - Fc = 10Hz
b3, a3 = signal.butter(4, Wpb, 'lowpass') # Design butter filter - Fc = 20Hz



# Retorna um tamanho de janela. Usado para fazer o janelamento e separação das amostras de Contração
def tamanhoJanela(TriggerFinal):
    flag = True
    for i, v in enumerate(TriggerFinal):
        if v >= 1.4 and flag == True:
            Yinf = i
            flag = False
        if v < 1 and flag == False:
            flag = True
            Ysup = i
            break
    Y = Ysup - Yinf
    return Y 

# Passando filtros no sinal
def PassaFiltros(DataFrameCH, F):
    '''    
    Retorna o SINAL filtrado:
    1 - Filtra sinal DC - Passa-Alta
    2 - Filtra sinal 60Hz
    3 - Retifica sinal
    4 - Filtra o sinal com um filtro Passa-Baixa
    '''
    filtradoDC = signal.filtfilt(b2, a2, DataFrameCH) # Passa um filtro PASSA-ALTA para remover nível DC do SINAL
    filtradoRede = signal.filtfilt(b1, a1, filtradoDC) # Passa um filtro NOTCH no SINAL para remover 60Hz
    retificado = np.abs(filtradoRede) # Retifica o SINAL filtrado
    passaBaixa = signal.filtfilt(b3, a3, retificado) # Passa um filtro PASSA-BAIXA no SINAL retificado
    if F == 1:
        return filtradoDC
    if F == 2:
        return filtradoRede
    if F == 3:
        return retificado
    if F == 4:
        return passaBaixa 
def CorrigeTrigger(atraso, TriggerDataFrame):
    '''
    Corrige o Trigger de acordo com o tempo de reação estimado do voluntário
    atraso -> atraso em amostras
              Em segundos: X = (atraso/2) [s]
    '''
    TR = [0]*atraso
    TR.extend(TriggerDataFrame)
    while len(TR) > len(TriggerDataFrame):
        del TR[len(TR) - 1]
    return TR 
def RemoveInicioColeta(TRIGGER, SINAL, J):
    '''
    Remove o inicio de coleta, o SINAL começa a partir da primeira borda de subida do TRIGGER. 
    J = 0 -> retorna o SINAL
    J = 1 -> retorna o TRIGGER
    '''
    ListaRemove = []
    S = list(SINAL)
    T = list(TRIGGER)
    for i in T:
        if i < 1.4:
            ListaRemove.append(i)
        if i > 1.4:
            break        
    DLista = int(len(ListaRemove))

    if J == 0:
        del S[:DLista]
        S.extend(ListaRemove)
        return S
    elif J == 1:
        del T[:DLista]
        T.extend(ListaRemove)
        return T 
def AmostrasSemRepouso(TriggerFinal, SINAL):
    '''
    Remove o tempo de repouso
    Retorna um vetor com todas as contrações. 
    '''
    T = list(TriggerFinal)
    S = list(SINAL)    
    NL = []
    flag = True    
    tJ = int(tamanhoJanela(T))
    for i, v in enumerate(T):
        if v > 1.4 and flag == True:
            NL.extend(S[i:i+tJ])
            flag = False
        if v < 1:
            flag = True
    return NL
def VetorDeAmostras(TriggerFinal, SINAL):
    '''
    Retorna o vetor com os SINAIS DE CONTRAÇÃO separados.
    Contem uma lista com N listas. Cada lista N é uma janela de contração.
    '''
    S = AmostrasSemRepouso(TriggerFinal, SINAL)
    Amostra = []
    tJ = int(tamanhoJanela(TriggerFinal))
    for T in range(0,60):
        Amostra.append(S[0:tJ])
        del S[0:tJ]
    return Amostra 

def SinalFinalGERAL(ListaDataFrame, SignalType):
    '''
    Recebe o bruto, sincroniza com o trigger e remove todo o inicio desnecessario da coleta.
    Retorna os sinais e od triggers finais de todas as coletas.
    O sinal pode assumir qualquer forma de acordo com o parâmetro 'SignalType'.
    SignalType -> Recebe valores 1, 2, 3 e 4 (Cada valor está de acordo com a função PassarFiltros()
    '''
    T1 = CorrigeTrigger(DelayT, ListaDataFrame[0]['Trigger'])
    SR11 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[0]['CH1'], SignalType), 0)
    SR12 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[0]['CH2'], SignalType), 0)
    SR13 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[0]['CH3'], SignalType), 0)
    SR14 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[0]['CH4'], SignalType), 0)

    T2 = CorrigeTrigger(DelayT, ListaDataFrame[1]['Trigger'])
    SR21 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[1]['CH1'], SignalType), 0)
    SR22 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[1]['CH2'], SignalType), 0)
    SR23 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[1]['CH3'], SignalType), 0)
    SR24 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[1]['CH4'], SignalType), 0)

    T3 = CorrigeTrigger(DelayT, ListaDataFrame[2]['Trigger'])
    SR31 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[2]['CH1'], SignalType), 0)
    SR32 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[2]['CH2'], SignalType), 0)
    SR33 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[2]['CH3'], SignalType), 0)
    SR34 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[2]['CH4'], SignalType), 0)

    T4 = CorrigeTrigger(DelayT, ListaDataFrame[3]['Trigger'])
    SR41 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[3]['CH1'], SignalType), 0)
    SR42 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[3]['CH2'], SignalType), 0)
    SR43 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[3]['CH3'], SignalType), 0)
    SR44 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[3]['CH4'], SignalType), 0)

    T5 = CorrigeTrigger(DelayT, ListaDataFrame[4]['Trigger'])
    SR51 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[4]['CH1'], SignalType), 0)
    SR52 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[4]['CH2'], SignalType), 0) 
    SR53 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[4]['CH3'], SignalType), 0)
    SR54 = RemoveInicioColeta(T1, PassaFiltros(ListaDataFrame[4]['CH4'], SignalType), 0)

    T6 = CorrigeTrigger(DelayT, ListaDataFrame[5]['Trigger'])
    SR61 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[5]['CH1'], SignalType), 0)
    SR62 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[5]['CH2'], SignalType), 0)
    SR63 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[5]['CH3'], SignalType), 0)
    SR64 = RemoveInicioColeta(T2, PassaFiltros(ListaDataFrame[5]['CH4'], SignalType), 0)

    T7 = CorrigeTrigger(DelayT, ListaDataFrame[6]['Trigger'])
    SR71 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[6]['CH1'], SignalType), 0)
    SR72 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[6]['CH2'], SignalType), 0)
    SR73 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[6]['CH3'], SignalType), 0)
    SR74 = RemoveInicioColeta(T3, PassaFiltros(ListaDataFrame[6]['CH4'], SignalType), 0)

    T8 = CorrigeTrigger(DelayT, ListaDataFrame[7]['Trigger'])
    SR81 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[7]['CH1'], SignalType), 0)
    SR82 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[7]['CH2'], SignalType), 0)
    SR83 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[7]['CH3'], SignalType), 0)
    SR84 = RemoveInicioColeta(T4, PassaFiltros(ListaDataFrame[7]['CH4'], SignalType), 0)

    # Trigger arrumado para cada coleta
    TC1 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[0]['Trigger']), PassaFiltros(ListaDataFrame[0]['CH1'], SignalType), 1)
    TC2 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[1]['Trigger']), PassaFiltros(ListaDataFrame[1]['CH1'], SignalType), 1)
    TC3 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[2]['Trigger']), PassaFiltros(ListaDataFrame[2]['CH1'], SignalType), 1)
    TC4 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[3]['Trigger']), PassaFiltros(ListaDataFrame[3]['CH1'], SignalType), 1)
    TC5 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[4]['Trigger']), PassaFiltros(ListaDataFrame[4]['CH1'], SignalType), 1)
    TC6 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[5]['Trigger']), PassaFiltros(ListaDataFrame[5]['CH1'], SignalType), 1)
    TC7 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[6]['Trigger']), PassaFiltros(ListaDataFrame[6]['CH1'], SignalType), 1)
    TC8 = RemoveInicioColeta(CorrigeTrigger(DelayT, ListaDataFrame[7]['Trigger']), PassaFiltros(ListaDataFrame[7]['CH1'], SignalType), 1)

    return TC1, SR11, SR12, SR13, SR14, TC2, SR21, SR22, SR23, SR24, TC3, SR31, SR32, SR33, SR34, TC4, SR41, SR42, SR43, SR44, TC5, SR51, SR52, SR53, SR54, TC6, SR61, SR62, SR63, SR64, TC7, SR71, SR72, SR73, SR74, TC8, SR81, SR82, SR83, SR84


def ZC(SINAL):
    zc = ((SINAL[:-1] * SINAL[1:]) < 0).sum()
    return float(zc) # Retorna a quantidade de vezes em que o SINAL cruzou o eixo Y = 0
def RMS(SINAL): 
    '''
    Retorna o valor RMS do SINAL DE CONTRAÇÃO
    '''
    S = np.array(SINAL)
    rms = np.sqrt(np.mean(S**2))
    return rms 
def VAR(SINAL):
    var = np.var(SINAL)
    return var
def SSC(SINAL):
    ssc = []
    E = 15
    S = list(SINAL)
    count = 0
    for i,v in enumerate(S):
        if i < (int(len(S))-1) and i > 0:
            
            if v > S[i-1] and v > S[i+1]:
                #if np.abs(v - S[i-1]) >= E or np.abs(v - S[i+1]) >= E:
                count += 1
            if v < S[i-1] and v < S[i+1]:
                #if np.abs(v - S[i-1]) >= E or np.abs(v - S[i+1]) >= E:
                count += 1
    return float(count)



def VetorATRIBUTOS(TriggerFinal, SINAL, Atributo):
    '''
    Retorna um vetor com os valores RMS de cada SINAL DE CONTRAÇÃO. 
    Retorna como -Pandas.Series-
    '''   
    A = VetorDeAmostras(TriggerFinal, SINAL)
    ListaAtributos = []
    if Atributo == 'RMS':
        for i, v in enumerate(A):
            ListaAtributos.append(RMS(A[i]))
        rms = pd.Series(ListaAtributos)
        return rms 
    if Atributo == 'ZC':
        for i, v in enumerate(A):
            ListaAtributos.append(ZC(np.array(A[i])))
        zc = pd.Series(ListaAtributos)
        return zc 
    if Atributo == 'VAR':
        for i, v in enumerate(A):
            ListaAtributos.append(VAR(np.array(A[i])))
        var = pd.Series(ListaAtributos)
        return var 
    if Atributo == 'SSC':
        for i, v in enumerate(A):
            ListaAtributos.append(SSC(np.array(A[i])))
        ssc = pd.Series(ListaAtributos)
        return ssc 

def DataFrameATRIBUTO(ListaDataFrame, Atributo):
    # Concatena todos os valores RMS de todas as coletas de um mesmo canal
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 1 - COLETA 1
    AtributoCH1_C1 = pd.concat([VetorATRIBUTOS(ListaDataFrame[0], ListaDataFrame[1], Atributo),VetorATRIBUTOS(ListaDataFrame[5], ListaDataFrame[6], Atributo),VetorATRIBUTOS(ListaDataFrame[10], ListaDataFrame[11], Atributo),VetorATRIBUTOS(ListaDataFrame[15], ListaDataFrame[16], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 2 - COLETA 1
    AtributoCH2_C1 = pd.concat([VetorATRIBUTOS(ListaDataFrame[0], ListaDataFrame[2], Atributo),VetorATRIBUTOS(ListaDataFrame[5], ListaDataFrame[7], Atributo),VetorATRIBUTOS(ListaDataFrame[10], ListaDataFrame[12], Atributo),VetorATRIBUTOS(ListaDataFrame[15], ListaDataFrame[17], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 3 - COLETA 1
    AtributoCH3_C1 = pd.concat([VetorATRIBUTOS(ListaDataFrame[0], ListaDataFrame[3], Atributo),VetorATRIBUTOS(ListaDataFrame[5], ListaDataFrame[8], Atributo),VetorATRIBUTOS(ListaDataFrame[10], ListaDataFrame[13], Atributo),VetorATRIBUTOS(ListaDataFrame[15], ListaDataFrame[18], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 4 - COLETA 1
    AtributoCH4_C1 = pd.concat([VetorATRIBUTOS(ListaDataFrame[0], ListaDataFrame[4], Atributo),VetorATRIBUTOS(ListaDataFrame[5], ListaDataFrame[9], Atributo),VetorATRIBUTOS(ListaDataFrame[10], ListaDataFrame[14], Atributo),VetorATRIBUTOS(ListaDataFrame[15], ListaDataFrame[19], Atributo)], ignore_index=True)
    
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 1 - COLETA 2
    AtributoCH1_C2 = pd.concat([VetorATRIBUTOS(ListaDataFrame[20], ListaDataFrame[21], Atributo),VetorATRIBUTOS(ListaDataFrame[25], ListaDataFrame[26], Atributo),VetorATRIBUTOS(ListaDataFrame[30], ListaDataFrame[31], Atributo),VetorATRIBUTOS(ListaDataFrame[35], ListaDataFrame[36], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 2 - COLETA 2
    AtributoCH2_C2 = pd.concat([VetorATRIBUTOS(ListaDataFrame[20], ListaDataFrame[22], Atributo),VetorATRIBUTOS(ListaDataFrame[25], ListaDataFrame[27], Atributo),VetorATRIBUTOS(ListaDataFrame[30], ListaDataFrame[32], Atributo),VetorATRIBUTOS(ListaDataFrame[35], ListaDataFrame[37], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 3 - COLETA 2
    AtributoCH3_C2 = pd.concat([VetorATRIBUTOS(ListaDataFrame[20], ListaDataFrame[23], Atributo),VetorATRIBUTOS(ListaDataFrame[25], ListaDataFrame[28], Atributo),VetorATRIBUTOS(ListaDataFrame[30], ListaDataFrame[33], Atributo),VetorATRIBUTOS(ListaDataFrame[35], ListaDataFrame[38], Atributo)], ignore_index=True)
    # Valor RMS de todas as 240 CONTRAÇÕES do CANAL 4 - COLETA 2
    AtributoCH4_C2 = pd.concat([VetorATRIBUTOS(ListaDataFrame[20], ListaDataFrame[24], Atributo),VetorATRIBUTOS(ListaDataFrame[25], ListaDataFrame[29], Atributo),VetorATRIBUTOS(ListaDataFrame[30], ListaDataFrame[34], Atributo),VetorATRIBUTOS(ListaDataFrame[35], ListaDataFrame[39], Atributo)], ignore_index=True)

    return AtributoCH1_C1, AtributoCH2_C1, AtributoCH3_C1, AtributoCH4_C1, AtributoCH1_C2, AtributoCH2_C2, AtributoCH3_C2, AtributoCH4_C2

def TabelaDeCaracteristicas(ValoresAtributo, Atributo):
    # Cria um DATAFRAME para colocar todas as CARACTERÍSTICAS do SINAL - COLETA 1
    FeaturesEMG_C1 = pd.DataFrame(0, index=range(0,240), columns=''.split())

    # Cria um DATAFRAME para colocar todas as CARACTERÍSTICAS do SINAL - COLETA 2
    FeaturesEMG_C2 = pd.DataFrame(0, index=range(0,240), columns=''.split())

    #Coloca todos os valores RMS de todos os canais em um DATAFRAME, sendo as CARACTERÍSTICAS do SINAL
    FeaturesEMG_C1[Atributo+'CH1'], FeaturesEMG_C1[Atributo+'CH2'], FeaturesEMG_C1[Atributo+'CH3'], FeaturesEMG_C1[Atributo+'CH4'] = ValoresAtributo[0], ValoresAtributo[1], ValoresAtributo[2], ValoresAtributo[3]
    FeaturesEMG_C2[Atributo+'CH1'], FeaturesEMG_C2[Atributo+'CH2'], FeaturesEMG_C2[Atributo+'CH3'], FeaturesEMG_C2[Atributo+'CH4'] = ValoresAtributo[4], ValoresAtributo[5], ValoresAtributo[6], ValoresAtributo[7]

    return FeaturesEMG_C1, FeaturesEMG_C2

def ConcatenaAtributos(*atributos):
    return pd.concat(atributos, axis=1)

def NormalizaDadosMATRIZ(DataFrame):
    df = DataFrame.copy()
    Max = float(df.max().max())
    for S in df:
        for i,v in enumerate(df[S]):
            df[S][i] = (100.0/Max)*float(v)
    return df

def NormalizaDadosCOLUNA(DataFrame):    
    df = DataFrame.copy()
    for S in df:
        Max = float(df[S].max())
        for i, v in enumerate(df[S]):
            df[S][i] = (100.0/Max)*float(v)
    return df


def TreinaSimples(TABELASCarac, TABELASResp):
    X_train, X_test, y_train, y_test = train_test_split(TABELASCarac, np.ravel(TABELASResp), test_size=0.25)
    Modelo = SVC()
    Modelo.fit(X_train, y_train)
    Predict = Modelo.predict(X_test)
    print(confusion_matrix(y_test,Predict))
    print(classification_report(y_test,Predict))
def TreinaMelhorParametro(TABELASCarac, TABELASResp):
    X_train, X_test, y_train, y_test = train_test_split(TABELASCarac, np.ravel(TABELASResp), test_size=0.25, stratify=np.ravel(TABELASResp))
    DicParametros =  {'C':[0.1,1,10,100,1000,10000, 100000, 10000000],'gamma':[100, 10, 1, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]}
    grid_cv = GridSearchCV(SVC(),DicParametros,refit=True,verbose=2)
    grid_cv.fit(X_train,y_train)
    pred = grid_cv.predict(X_test)
    print(grid_cv.best_params_)
    print(confusion_matrix(y_test,pred))
    print(classification_report(y_test,pred))
    print(grid_cv.best_params_)
    X_set, y_set = X_test, y_test
    X1, X2 = np.meshgrid(np.arange(start = X_set.iloc[:,0:0].min() - 1, stop = X_set.iloc[:,0:0].max() + 1, step = 0.01),
                         np.arange(start = X_set.iloc[:,0:1].min() - 1, stop = X_set.iloc[:,0:1].max() + 1, step = 0.01))
    plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
                 alpha = 0.2, cmap = ListedColormap(('red', 'green', 'blue')))
    plt.xlim(X1.min(), X1.max())
    plt.ylim(X2.min(), X2.max())
    for i, j in enumerate(np.unique(y_set)):
        plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                    c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
    plt.title('Logistic Regression (Test set)')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.legend()
    plt.show()
def TreinaValidacaoCruzada(TABELASCarac, TABELASResp):
    R = np.ravel(TABELASResp).copy()
    kf = StratifiedKFold(n_splits=10, shuffle=True)
    kfTenFold = kf.split(TABELASCarac, R)
    for train_index, test_index in kf.split(TABELASCarac, R):
        print("\n\nTRAIN:", train_index, "\nTEST:", test_index)
        X_train2, X_test2 = TABELASCarac.index[train_index], TABELASCarac.index[test_index]
        y_train2, y_test2 = TABELASResp.index[train_index], TABELASResp.index[test_index]

    DicParametros = {'C':[0.1,1,10,100,1000], 'gamma':[1,0.1,0.01,0.001]}
    grid_cv = GridSearchCV(SVC(),DicParametros, cv=kfTenFold)
    grid_cv.fit(TABELASCarac,R)
    grid_cv.best_params_

    CrossV = cross_val_score(grid_cv.best_estimator_, TABELASCarac, R, scoring='accuracy', cv=kf.split(Carac_VAR_Coleta2, R))
    MediaAcuracia = CrossV.mean()
    CrossV2 = cross_val_predict(grid_cv.best_estimator_, TABELASCarac, R, cv=kf.split(TABELASCarac, R))
    print(CrossV)
    print(MediaAcuracia)
    print(confusion_matrix(R,CrossV2))
    print(classification_report(R,CrossV2))
    #sns.heatmap(confusion_matrix(np.ravel(TABELASResp),CrossV2), cmap='hot', annot=True, fmt="d", linecolor='gray',linewidths=.5)

def ExtraiNovoAtributo(DATAFRAME, Atributo):
    df1 = DATAFRAME[Atributo+'CH1']
    df2 = DATAFRAME[Atributo+'CH2']
    df3 = DATAFRAME[Atributo+'CH3']
    df4 = DATAFRAME[Atributo+'CH4']
    NA1 = (np.abs(df1-df2))
    NA2 = (np.abs(df1-df3))
    NA3 = (np.abs(df1-df4))
    NA4 = (np.abs(df2-df3))
    NA5 = (np.abs(df2-df4))
    NA6 = (np.abs(df3-df4))
    return ConcatenaAtributos(NA1, NA2, NA3, NA4, NA5, NA6)

##########################################################################################################################################################################
##########################################################################################################################################################################



VOLUNTARIO = SinalVoluntario('LH')
VOLUNTARIO_Coleta = VOLUNTARIO.CarregaDados()
VOLUNTARIO_Resp = VOLUNTARIO.CarregaRespostas()
VOLUNTARIO_Respostas1 = VOLUNTARIO_Resp[:240]
VOLUNTARIO_Respostas2 = VOLUNTARIO_Resp[240:].reset_index(drop=True)

VOLUNTARIO_SinalFinalBruto = SinalFinalGERAL(VOLUNTARIO_Coleta,2)
VOLUNTARIO_SinalFinalRetificado = SinalFinalGERAL(VOLUNTARIO_Coleta,3)

VOLUNTARIO_ZC = DataFrameATRIBUTO(VOLUNTARIO_SinalFinalBruto, 'ZC')
VOLUNTARIO_RMS = DataFrameATRIBUTO(VOLUNTARIO_SinalFinalRetificado, 'RMS')
VOLUNTARIO_VAR = DataFrameATRIBUTO(VOLUNTARIO_SinalFinalBruto, 'VAR')
VOLUNTARIO_SSC = DataFrameATRIBUTO(VOLUNTARIO_SinalFinalBruto, 'SSC')

VOLUNTARIO_TabelasZC = TabelaDeCaracteristicas(VOLUNTARIO_ZC, 'ZC')
VOLUNTARIO_TabelasRMS = TabelaDeCaracteristicas(VOLUNTARIO_RMS, 'RMS')
VOLUNTARIO_TabelasVAR = TabelaDeCaracteristicas(VOLUNTARIO_VAR, 'VAR')
VOLUNTARIO_TabelasSSC = TabelaDeCaracteristicas(VOLUNTARIO_SSC, 'SSC')

Carac_ZC_Coleta1, Carac_ZC_Coleta2 = NormalizaDadosCOLUNA(VOLUNTARIO_TabelasZC[0]), NormalizaDadosCOLUNA(VOLUNTARIO_TabelasZC[1])
Carac_RMS_Coleta1, Carac_RMS_Coleta2  = NormalizaDadosCOLUNA(VOLUNTARIO_TabelasRMS[0]), NormalizaDadosCOLUNA(VOLUNTARIO_TabelasRMS[1])
Carac_VAR_Coleta1, Carac_VAR_Coleta2  = NormalizaDadosCOLUNA(VOLUNTARIO_TabelasVAR[0]), NormalizaDadosCOLUNA(VOLUNTARIO_TabelasVAR[1])
Carac_SSC_Coleta1, Carac_SSC_Coleta2  = NormalizaDadosCOLUNA(VOLUNTARIO_TabelasSSC[0]), NormalizaDadosCOLUNA(VOLUNTARIO_TabelasSSC[1])

TabelaDeAtributos_VOLUNTARIO_1 = ConcatenaAtributos(Carac_RMS_Coleta1, Carac_ZC_Coleta1, Carac_VAR_Coleta1, Carac_SSC_Coleta1)
TabelaDeAtributos_VOLUNTARIO_2 = ConcatenaAtributos(Carac_RMS_Coleta2, Carac_ZC_Coleta2, Carac_VAR_Coleta2, Carac_SSC_Coleta2)

NT = ExtraiNovoAtributo(Carac_SSC_Coleta1, 'SSC')

############################################################################################################################################################################
############################################################################################################################################################################




RMS_VAR1 = ConcatenaAtributos(Carac_RMS_Coleta1, Carac_VAR_Coleta1)
RMS_SSC1 = ConcatenaAtributos(Carac_RMS_Coleta1, Carac_SSC_Coleta1)
RMS_ZC1 = ConcatenaAtributos(Carac_RMS_Coleta1, Carac_ZC_Coleta1)
VAR_SSC1 = ConcatenaAtributos(Carac_VAR_Coleta1, Carac_SSC_Coleta1)
VAR_ZC1 = ConcatenaAtributos(Carac_VAR_Coleta1, Carac_ZC_Coleta1)
SSC_ZC1 = ConcatenaAtributos(Carac_SSC_Coleta1, Carac_ZC_Coleta1)
Co1 = ConcatenaAtributos(RMS_SSC1)

RMS_VAR2 = ConcatenaAtributos(Carac_RMS_Coleta2, Carac_VAR_Coleta2)
RMS_SSC2 = ConcatenaAtributos(Carac_RMS_Coleta2, Carac_SSC_Coleta2)
RMS_ZC2 = ConcatenaAtributos(Carac_RMS_Coleta2, Carac_ZC_Coleta2)
VAR_SSC2 = ConcatenaAtributos(Carac_VAR_Coleta2, Carac_SSC_Coleta2)
VAR_ZC2 = ConcatenaAtributos(Carac_VAR_Coleta2, Carac_ZC_Coleta2)
SSC_ZC2 = ConcatenaAtributos(Carac_SSC_Coleta2, Carac_ZC_Coleta2)
Co2 = ConcatenaAtributos(RMS_SSC2)


Carac_TODOS_CH1 = ConcatenaAtributos(Carac_RMS_Coleta1['RMSCH1'], Carac_SSC_Coleta1['SSCCH1'], Carac_VAR_Coleta1['VARCH1'], Carac_ZC_Coleta1['ZCCH1'])
Carac_TODOS_CH2 = ConcatenaAtributos(Carac_RMS_Coleta1['RMSCH2'], Carac_SSC_Coleta1['SSCCH2'], Carac_VAR_Coleta1['VARCH2'], Carac_ZC_Coleta1['ZCCH2'])
Carac_TODOS_CH3 = ConcatenaAtributos(Carac_RMS_Coleta1['RMSCH3'], Carac_SSC_Coleta1['SSCCH3'], Carac_VAR_Coleta1['VARCH3'], Carac_ZC_Coleta1['ZCCH3'])
Carac_TODOS_CH4 = ConcatenaAtributos(Carac_RMS_Coleta1['RMSCH4'], Carac_SSC_Coleta1['SSCCH4'], Carac_VAR_Coleta1['VARCH4'], Carac_ZC_Coleta1['ZCCH4'])


def PCA(X, y, N, ):
    X = np.array(Carac_TODOS_CH4)
    y = np.array(VOLUNTARIO_Respostas1.copy())
    pca = PCA(n_components=N)
    principalComponents = pca.fit_transform(X)
    principalDf4 = pd.DataFrame(data = principalComponents, columns = ['CH4_PC1', 'CH4_PC2'])
    finalDf = principalDf.copy()
    finalDf['Resposta'] = VOLUNTARIO_Respostas1.copy()

    PrincipaisComponentes = ConcatenaAtributos()


fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Componente Principal 1', fontsize = 15)
ax.set_ylabel('Componente Principal 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
Respostas = ['Pinçar', 'Supinar', 'Pronar', 'Fechar', 'Estender', 'Flexionar']
colors = ['green', 'royalblue', 'red', 'darkorange', 'darkmagenta', 'sienna']
for Resposta, color in zip(Respostas,colors):
    indicesToKeep = finalDf['Resposta'] == Resposta
    ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1'], finalDf.loc[indicesToKeep, 'principal component 2'], c = color, s = 50)
ax.legend(Respostas)
ax.grid()
plt.show()


R = np.ravel(VOLUNTARIO_Respostas1.copy())
kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=2)
kfTenFold = kf.split(PrincipaisComponentes, R)
DicParametros = {'C':[0.1,1,10,100,1000], 'gamma':[1,0.1,0.01,0.001]} # [{'C':[0.1,1,10,100,1000], 'kernel':['linear']}, {'C':[0.1,1,10,100,1000], 'kernel':['rbf'], 'gamma':[1,0.1,0.01,0.001]}]
grid_cv = GridSearchCV(SVC(),DicParametros, cv=kfTenFold)
grid_cv.fit(PrincipaisComponentes,R)
grid_cv.best_params_
CrossV = cross_val_score(grid_cv.best_estimator_, PrincipaisComponentes, R, scoring='accuracy', cv=kf.split(PrincipaisComponentes, R))
MediaAcuracia = CrossV.mean()
CrossV2 = cross_val_predict(grid_cv.best_estimator_, PrincipaisComponentes, R, cv=kf.split(PrincipaisComponentes, R))
print(CrossV)
print(MediaAcuracia)
print(confusion_matrix(R,CrossV2))
print(classification_report(R,CrossV2))


Pred = grid_cv.predict(Co2)
print(confusion_matrix(VOLUNTARIO_Respostas2,Pred))
print(classification_report(VOLUNTARIO_Respostas2,Pred))



PrincipaisComponentes['Resposta'] = VOLUNTARIO_Respostas1
sns.pairplot(PrincipaisComponentes,hue='Resposta', aspect=1, palette=dict(Pinçar = 'green', Supinar = 'royalblue', Pronar = 'red',Fechar = 'darkorange', Estender = 'darkmagenta', Flexionar = 'sienna'))
plt.show()

























for train_index, test_index in kf.split(Carac_RMS_Coleta1, R):
    print("\n\nTRAIN:", train_index, "\nTEST:", test_index)
    X_train2, X_test2 = Carac_RMS_Coleta1.index[train_index], Carac_RMS_Coleta1.index[test_index]
    y_train2, y_test2 = VOLUNTARIO_Respostas1.index[train_index], VOLUNTARIO_Respostas1.index[test_index]

