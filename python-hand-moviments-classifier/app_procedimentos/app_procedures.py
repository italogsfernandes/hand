#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:06:46 2018

@author: italo
"""
#%% Importing the libraries
import pandas as pd # reading files
import numpy as np # handling numerical data
import matplotlib.pyplot as plt # Plotting
from scipy import signal

#%% Adding the path to datasets
HAND_MOVIMENTS_NAMES = ["Supinar", "Pronar", "Pinçar", "Fechar", "Estender", "Flexionar"]

#%% Importing the dataset
# TODO: perguntar julia sobre os protocolos dessas coletas,
# por que 11, 12, 13, 14, 21, 22, 23, 24?
file_name = '../../datasets/coletas/Eber/Eber11-Final.txt'
dataset = pd.read_table(file_name, sep=';', header=None)
dataset.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
emg_channels = dataset.iloc[:, :-2].values
emg_trigger = dataset.iloc[:, -2].values

file_name_targets = '../../datasets/coletas/Eber/Eber11-Resposta.txt'
targets = pd.read_table(file_name_targets, header=None)
targets = targets.iloc[:, :].values.ravel()
targets_str = []
for target in targets:
    targets_str.append(HAND_MOVIMENTS_NAMES[target-1])

#%% Constantes dos sinais
# Tempo de atraso (em amostras) no TRIGER para sincronização SINAL/TRIGGER
delay_trigger = 500
fs = 2000  # Frequência de amostragem (Hz)fa = 

#%% Correcting the triger
# TODO: perguntar julia oq vai ser feito desse atraso
emg_trigger_corrected = np.append(arr = np.zeros(delay_trigger),
                                  values = emg_trigger[:-delay_trigger])

#%% Optional: Plotting the data
'''
fig = plt.figure()
axes = [None for i in range(4)]
for i in range(4):
    axes[i] = plt.subplot(4,1,i+1)
    plt.plot(emg_channels[12000:80000,i])
    plt.plot(emg_trigger_corrected[12000:80000]*100)
    plt.title('Ch ' + str(i+1))
    plt.ylim((-1000,1000))
    plt.grid()

axes[0].get_shared_x_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].get_shared_y_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].set_xticklabels([])
axes[1].set_xticklabels([])
axes[2].set_xticklabels([])
plt.show()
'''
#%% Filtering
# TODO: Perguntar a julia sobre a filtragem, quais filtros tenho que passar?
# quais frequencias? quais caracteristicas?

# Parâmetros para a construção dos filtros
Fnotch = 60.0  # Frequência para remoer com o filtro NOTCH - Remover interferência da rede
Fpa = 10.0 # Frequência de corte do filtro PASSA-ALTA - Remoção do Offset gerado pelo sinal DC
Fpb = 20.0 # Frequência de corte do filtro PASSA-BAIXA - Suavização do sinal
Q = 1  # Fator de qualidade do filtro NOTCH

# Frequência normalizada:
Wnotch = Fnotch/(fs/2) # Para o filtro NOTCH
Wpb = Fpb/(fs/2) # Para o filtro PASSA-BAIXA
Wpa = Fpa/(fs/2) # Para o filtro PASSA-ALTA

# Construção de filtros
b1, a1 = signal.iirnotch(Wnotch, Q) # Design notch filter - Fc = 60Hz
b2, a2 = signal.butter(2, Wpa, 'highpass') # Design butter filter - Fc = 10Hz
b3, a3 = signal.butter(4, Wpb, 'lowpass') # Design butter filter - Fc = 20Hz

#%% Passando os filtros
# Passa um filtro PASSA-ALTA para remover nível DC do SINAL
emg_filtered_dc = np.zeros(emg_channels.shape)
for ch in range(4):
    emg_filtered_dc[:,ch] = signal.filtfilt(b2, a2, emg_channels[:, ch])

# Passa um filtro NOTCH no SINAL para remover 60Hz
emg_filtered_60hz = np.zeros(emg_channels.shape)
for ch in range(4):
    emg_filtered_60hz[:,ch] = signal.filtfilt(b1, a1, emg_filtered_dc[:, ch])

# Retifica o SINAL filtrado
emg_retificado = np.abs(emg_filtered_60hz) 

# low-pass filtered
emg_smooth = np.zeros(emg_channels.shape)
for ch in range(4):
    emg_smooth[:, ch] = signal.filtfilt(b3, a3, emg_retificado[:, ch]) # Passa um filtro PASSA-BAIXA no SINAL retificado

#%% Optional: Testando filtros
'''
plt.subplot(2,1,1)
plt.plot(emg_channels[12000:80000,0])
plt.grid()
plt.subplot(2,1,2)
plt.plot(emg_filtered_dc[12000:80000,0])
#plt.plot(emg_filtered_60hz[12000:80000,0])
#plt.plot(emg_retificado[12000:80000,0])
#plt.plot(emg_smooth[12000:80000,0])
plt.grid()
plt.show()
'''
#%% Contraction sites
contractions_onsets = []
contractions_offsets = []
for i in range(1,emg_channels.shape[0]):
    # Borda 0 -> 1
    if emg_trigger_corrected[i-1] < 1 and emg_trigger_corrected[i] >= 1:
        contractions_onsets.append(i)
    # Borda 1 -> 0
    if emg_trigger_corrected[i-1] > 1 and emg_trigger_corrected[i] <= 1:
        contractions_offsets.append(i)
       
#%% Feature Extraction
#TODO: Perguntar julia como calcular WL e SSC
rms = np.zeros((len(targets), 4), dtype=float) # root mean square (RMS)
zc = np.zeros((len(targets), 4), dtype=float) # zero crossing (ZC)
mav = np.zeros((len(targets), 4), dtype=float) # mean absolute value (MAV)
#wl = np.zeros((len(targets), 4), dtype=float) # waveform length (WL)
var = np.zeros((len(targets), 4), dtype=float) # variance (VAR)
#ssc = np.zeros((len(targets), 4), dtype=float) # slope sign changes (SSC)

#%% Extraindo as caracteristicas
#TODO: Perguntar julia se estou estraindo o rms, zc, mav e var do sinal certo
for i in range(len(targets)):
    for ch in range(4):
        #RMS
        rms[i,ch] = np.sqrt(np.mean(np.square(
           emg_filtered_60hz[contractions_onsets[i]:contractions_offsets[i],ch]
           )))
        #ZC
        s3= np.sign(
         emg_filtered_60hz[contractions_onsets[i]:contractions_offsets[i],ch])  
        s3[s3==0] = -1     # replace zeros with -1  
        zc[i,ch] = (np.where(np.diff(s3)))[0].shape[0]
        #MAV
        mav[i, ch] = np.mean(np.abs(
                emg_retificado[contractions_onsets[i]:contractions_offsets[i],ch]
                ))
        #VAR
        var[i, ch] = np.var(
                emg_filtered_60hz[contractions_onsets[i]:contractions_offsets[i],ch]
                )

#Explicações:
#    RMS:
#        sqrt(mean(square(vetor)))
#    ZC:
#             a = [ 1,  2,  1,  1, -3, -4,  7,  8,  9, 10, -2,  1, -3,  5,  6,  7,-10]
#        sign() = [ 1,  1,  1,  1, -1, -1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1]
#        diff() =     [ 0,  0,  0, -2,  0,  2,  0,  0,  0, -2,  2, -2,  2,  0,  0, -2]
#        where() = (array([ 3,  5,  9, 10, 11, 12, 15]),)
#        where()[0].shape[0] = 7
#    The number of zero crossing should be 7, but because sign() 
#    returns 0 if 0 is passed, 1 for positive, and -1 for negative values,
#    diff() will count the transition containing zero twice.
#    An alternative might be:
#
#TODO: terminar a extração de caracteristicas
#%% Dataset Pre-processed
X = np.append(arr=rms, values=zc, axis=1)
X = np.append(arr=X, values=mav, axis=1)
X = np.append(arr=X, values=var, axis=1)
#X = rms # testando somente com rms como entrada
#y = targets # saida = targets
#y = y.reshape(-1,1).astype(float)

y = np.array(targets_str)

#y = np.zeros((targets.shape[0],6),dtype=bool)

#for n in range(1,7):
#    y[:,n-1] = (targets == n).astype(bool)

# Encoding categorical data
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
labelencoder_Y = LabelEncoder()
labelencoder_Y.fit(HAND_MOVIMENTS_NAMES)
y = labelencoder_Y.transform(y)
#onehotencoder = OneHotEncoder(categorical_features = [0])
#y = onehotencoder.fit_transform(y).toarray()

#%%
y = np.zeros((targets.shape[0],6),dtype=bool)

for n in range(6):
    y[:,n] = (targets == n).astype(bool)

#%% Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

#%% Finalmente montando a rede neural
#%% Importing the Keras libraries and packages
import keras
from keras.models import Sequential
from keras.layers import Dense

# Initialising the ANN
classifier = Sequential()

# Adding the layers
# Adding the input layer and the first hidden layer
# 4 entradas RMS_ch1, RMS_ch2, RMS_ch3, RMS_ch4
classifier.add(Dense(output_dim = 29, init = 'uniform', activation = 'relu', input_dim = 16))
# Adding the second hidden layer
classifier.add(Dense(output_dim = 13, init = 'uniform', activation = 'relu'))
# Adding the output layer
classifier.add(Dense(output_dim = 6, init = 'uniform', activation = 'sigmoid'))

# Compiling the ANN
classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

#%% Fitting the ANN to the Training set
classifier.fit(X_train, y_train, batch_size = 10, nb_epoch = 100, verbose=1)

#%% Making the predictions and evaluating the model

#%% Predicting the Test set results
y_pred = classifier.predict_classes(X_train)#.reshape(48,1)
#y_pred = classifier.predict(X_train,verbose=1)

# confusion matrix
#%%
def get_labeled_matriz(sparce):
    dense = np.zeros((sparce.shape[0],1))
    for i in range(sparce.shape[0]):
        ind = np.where(sparce[i,:] == (sparce[i,:]).max())[0][0]
        dense[i] = ind + 1
    return dense

#%% Making the Confusion Matrix
from sklearn.metrics import confusion_matrix
y_pred_l = y_pred#get_labeled_matriz(y_pred)
y_test_l = get_labeled_matriz(y_train)
cm = confusion_matrix(y_test_l, y_pred_l)

cole = np.append(arr=y_pred_l, values=y_test_l, axis=1)
#%%
lines = np.zeros((6,1))
columns = np.zeros((1,7))
total_acertos = 0

for i in range(6):
    lines[i,0] = cm[i,i] / np.sum(cm[i,:])
    columns[0,i] = cm[i,i] / np.sum(cm[:,i])
    total_acertos += cm[i,i]

t_acc = total_acertos / np.sum(cm)
columns[0,6] = t_acc
cm2 = np.append(arr=cm, values=lines, axis=1)
cm2 = np.append(arr=cm2, values=columns, axis=0)