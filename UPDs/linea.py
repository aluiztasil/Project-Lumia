from importlib.metadata import files
from scipy.stats import linregress
import pandas as pd
import numpy as np
import scipy as sp
from collections import namedtuple
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
class Linea():
    
    def __init__(self, file, other_info={}, dados={},heat_rate=[],corrected_data = {},correction={},pre_heat=False):
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        self.data = dados
        self.file = file
        self.pre_heat = pre_heat
        self.heat_rate = heat_rate
        self.other_info = other_info
        self.corrected_data = corrected_data
        self.correction = correction

    def add_treated_data(self):
        data = pd.read_csv(self.file)
        self.data = data
        return "Data Added"

    def clean_misc(self):
        self.pre_heat = False
        self.heat_rate = []
        self.other_info = {}
        self.corrected_data = {}
        self.correction = {}

    #_______________________________________________________________________________________________________________

    def load_TL(self, pre_heat=False, pre_heat_value=25, points_equal_temp=True,trimm_by='\t', lim_init = 4):
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        arquivo=self.file
        if arquivo:
            with open(arquivo, 'r') as f:#Abre arquivo
                matrix = [[item for item in line.split(trimm_by)] for line in f.readlines()[lim_init:-1]]#Quebra linhas e colunas por tabulação
            matrixNumpy = np.array(matrix)                #matriz numpy
            curve={}                                     #variavel dicionario auxiliar
            for i in range(len(matrixNumpy.T)):       #É a iteração nas colunas pelo intervalo da matrix transposta do resultado
                lab=matrixNumpy[:,i]               #seleciona a coluna toda
                lista=[]                         #lista auxiliar
                for lin in lab:                   #iteração de valor em valor
                    try:                         #evita bugs e erros por conversão falha
                        lista.append(int(lin))      #converte str para int
                    except:
                        lista.append(np.nan)      #caso vazio e erro adiciona NAN
                if i == 0:                        #a primeira coluna é temperatura
                    if pre_heat == False:          #Teste logico de preheat para soma de Temperatura inicial
                        curve.setdefault('Temperatura',lista) #Adciona o rótulo temperatura ao dicionario
                    else:
                        lista = np.array(lista) + pre_heat_value #soma o preheat em um nd array
                        lista = list(lista)
                        curve.setdefault('Temperatura',lista) #adiciona a temperatura ao dicinario
                else:
                    curve.setdefault('Curva {0}'.format(i),lista) #Adiciona as curvas ao dicionario
            data=pd.DataFrame(curve, index=curve['Temperatura']) #cria um pd.dataframe com os resultados
            self.data = data
            
            return data
        else:
            
            return print('Please add a VALID file to when itiating Linea')
    #_______________________________________________________________________________________________________________
    def get_info(self, info_line,trimm_by='\t',lim_init=0):
        """ Extracts the information from the heading of the .txt data file, please inform Which id the row identifier"""
        arquivo = self.file
        with open(arquivo, 'r') as f:#Abre arquivo
            matrix = [[item for item in line.split(trimm_by)] for line in f.readlines()[lim_init:-1]]#Quebra linhas e colunas por tabulação
            gotten_info={}
        for information in matrix:
            if information[0] == info_line:
                info=[]
                for number in information[1:]:
                    number = number.strip()
                    try:
                        info.append(float(number))
                    except ValueError:
                        info.append(float(number.replace(',','.')))
                gotten_info.setdefault(info_line,info)
        self.other_info.update(gotten_info)
        
        return gotten_info
    #_______________________________________________________________________________________________________________
    def temperature_and_peak_extraction(self):
        """ Extracts the peak temperature and the max TL intensity """
        temperature_peak = []
        peak_values = []
        peak_temperatures = []

        for curva in self.data.columns[1:]:
            termperature = int(self.data[self.data[curva]==max(self.data[curva])]['Temperatura'])
            peak_value = max(self.data[curva])
            peak_values.append(peak_value) #goes to self
            peak_temperatures.append(termperature) #goes to self
            temperature_peak.append((termperature,peak_value)) #user returned
        temp_peak={'Peak Temperatures':peak_temperatures,'Peak Values':peak_values}
        self.other_info.update(temp_peak)
        
        return temperature_peak
    #_______________________________________________________________________________________________________________
    def linea_regression(self,skip=1,stop_point=5):
        """Performs a linear regression with the irradiation time versus TL peak, it requires the peak the information to be
        previously extracted, and extrapolates it into the domain of interest"""
        from scipy.stats import linregress
        regression_vector = []
        peak_values = self.other_info['Peak Values'][skip:stop_point]
        irrad_time_slice = self.other_info['Irrad. Time'][skip:stop_point]
        irrad_time_ = self.other_info['Irrad. Time']#[skip:]
        lin_reg = linregress(irrad_time_slice,peak_values)
        a = lin_reg.slope
        b = lin_reg.intercept
        for time in irrad_time_:
            if time == 0:
                extrapolate = np.nan
            else:
                extrapolate =  a*time + b
            regression_vector.append(extrapolate)
        self.other_info['Regression Vector']= regression_vector
        
        return regression_vector
    #_______________________________________________________________________________________________________________
    def correction_vector_calculation(self,provided_irr_time=[],skip=1,start_point=5):
        """Calculates the correction factor vector for the riso detector for the dataset """
        if provided_irr_time:
            self.other_info['Irrad. Time'] = provided_irr_time
        else:
            try:
                self.get_info(info_line='Irrad. Time')
            except KeyError:
                return 'Unable to get the required information to execute this function'
        try:
            peaks = self.other_info['Peak Values']
        except KeyError:
            temporary = self.temperature_and_peak_extraction()
            peaks = [x[1] for x in temporary]
        try:
            regression = self.other_info['Regression Vector']
        except KeyError:
            regression = self.linea_regression()

        correction_factor = np.array(regression)/np.array(peaks)
        correction_factor = list(correction_factor)
        self.other_info['Correction Factor'] = correction_factor
        try:
            regress = linregress(self.other_info['Irrad. Time'][start_point:],correction_factor[start_point:])
            self.correction = {'a':regress.slope,'b':regress.intercept,'r^2':regress.rvalue}
        except ValueError:
            print('Value Error')
            self.correction = 'Value Error'

        return correction_factor
    #_______________________________________________________________________________________________________________
    def correct_spectrum(self, overwrite=False):
        """Corrects the spectrum and creates a corrected dataframe"""
        self.get_info(info_line='Irrad. Time')
        try:
            correction = self.other_info['Correction Factor']
        except KeyError:
            correction = self.correction_vector_calculation()
        self.corrected_data['Temperatura'] = self.data['Temperatura']
        for correct, column in zip(correction,self.data.columns[1:]):
            if np.isnan(correct):
                self.corrected_data[column] = self.data[column]
            else:
                self.corrected_data[column] = correct * self.data[column]
        self.corrected_data = pd.DataFrame(self.corrected_data)
        if overwrite:
            self.data = self.corrected_data

        return self.corrected_data
    #_______________________________________________________________________________________________________________
    def split_samples(self,size=24,information_trimm='Rate'):
        # actual_size = size
        feature=[]
        rates = list(set(dados_.other_info['Rate']))
        # times = list(set(self.other_info['Irrad. Time']))
        overall=(len(self.data.columns) - 1)/size
        size=24
        for j, rate in enumerate(rates,start=1):
            feature=[]
            if j == 1:
                false_size= 27
                for i in range(3,false_size):
                    feature.append('Curva {0}'.format(i))
                feature.insert(0,'Temperatura')
                print(feature)
                df_tosave={}
                for ff in feature:
                    df_tosave.setdefault(ff,dados_.data[ff])
                df_tosave = pd.DataFrame(df_tosave)

                df_tosave.to_csv('LiF Heating_rate-{0}.csv'.format(rate),index=False)
            else:
                actual_size = size*j + 3
                past_size = size * (j-1) + 3
                for i in range(past_size,actual_size):
                    feature.append('Curva {0}'.format(i))
                feature.insert(0,'Temperatura')
                df_tosave={}
                for ff in feature:
                    df_tosave.setdefault(ff,dados_.data[ff])
                df_tosave = pd.DataFrame(df_tosave)
                df_tosave.to_csv('LiF Heating_rate-10.csv'.format(rate),index=False)



              