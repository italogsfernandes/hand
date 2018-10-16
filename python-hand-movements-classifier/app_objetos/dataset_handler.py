# -*- coding: utf-8 -*-
import sys # path and python version functions
import pandas as pd # reading files
import numpy as np # handling numerical data
# from scipy import signal # signal processing
# import matplotlib.pyplot as plt # Plots

# Adding the path to datasets
#sys.path.append('../datasets/coletas/Eber')
#sys.path.append('..\\datasets\\coletas\\Eber\\')

HAND_MOVIMENTS_NAMES = ["Supinar", "Pronar", "Pinçar", "Fechar", "Estender", "Flexionar"]

class volunter_dataset:
    def __init__(self, volunter_pseudo):
        self.pseudo = volunter_pseudo
        self.data_files = []
        self.target_files = []
        self.dataframes = None
        self.targets = None
        self.generate_file_names()

    def generate_file_names(self):
        for i in range(1,3):
            for j in range(1,5):
                self.data_files.append(self.pseudo+str(i)+str(j)+'-Final.txt')
                self.target_files.append(self.pseudo+str(i)+str(j)+'-Resposta.txt')

    def load_data(self):
        lista = np.arange(760000) # index para o DATAFRAME.
        self.dataframes = []
        for file_name in self.data_files:
            dados = pd.read_table(file_name, sep=';', header=None)
            print(type(dados))
            df = pd.DataFrame(0, index=lista, columns='CH1 CH2 CH3 CH4 Trigger'.split())
            df['CH1'], df['CH2'], df['CH3'], df['CH4'], df['Trigger'] = \
                dados[0], dados[1], dados[2], dados[3], dados[4]
            self.dataframes.append(df)

    def  load_answers(self):
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
        for file_name in self.target_files:
            respostas = np.array(pd.read_table(file_name, header=None))
            for resposta in respostas:
                listaresposta.append(HAND_MOVIMENTS_NAMES[resposta+1])
        TargetEMG = pd.DataFrame(0, index=np.arange(0,480), columns=''.split())
        TargetEMG['Resposta'] = listaresposta
        self.targets = TargetEMG

def main():
    my_dataset = volunter_dataset("Eber")
    print("Carregando dados")
    my_dataset.load_data()
    print("Dados carregados")
    #print(my_dataset.dataframes)
    print(type(my_dataset.dataframes[0]))

    # my_dataset = VOLUNTARIO.CarregaDados()

if __name__ == '__main__':
    main()
