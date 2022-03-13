import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import openpyxl


def load_transform_df(data_folder):
    df=pd.DataFrame()
    for file in os.listdir(data_folder):
        if 'avg_from_' in file:
            df = pd.concat([df, pd.read_csv(data_folder + file, delimiter=',' )])            
    df['czas']  = pd.to_datetime(df['czas'])
    
    temp_zuz = pd.read_csv((data_folder+'temp_zuz.csv'), delimiter=',')
    temp_zuz['czas'] = pd.to_datetime(temp_zuz['Czas']).dt.tz_localize('CET', ambiguous = 'NaT')
    temp_zuz = temp_zuz.drop('Czas', axis = 1)
    
    opis = pd.read_excel((data_folder+'opis_zmiennych.xlsx'), engine='openpyxl')
    opis_zip = zip(opis.Tagname.str.lower(), opis.opis.values)
    opis_dict = dict(opis_zip)
    opis_dict['037tix00254.daca.pv'] = 'TEMP. WODY ZASIL.OBIEG PZ 1'
    opis_dict['037tix00264.daca.pv'] = 'TEMP. WODY ZASIL.OBIEG PZ 2'
    df.rename(columns=opis_dict, inplace=True)
    
    df_tidy = pd.DataFrame()
    df_tidy['czas'] = pd.to_datetime(df['czas'])
    df_tidy['woda_powrotna_przeplyw'] = (
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ7'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ8'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ9'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ10'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ11'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ12'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ13'] + 
        df['WODA CHŁODZĄCA DO KOLEKTOR KZ15']
    )
    df_tidy['woda_powrotna_temp'] = (
        df['WODA POWROTNA KOLEKTORA KZ7']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ7'] + 
        df['WODA POWROTNA KOLEKTORA KZ8']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ8'] + 
        df['WODA POWROTNA KOLEKTORA KZ9']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ9'] +   
        df['WODA POWROTNA KOLEKTORA KZ10']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ10'] +   
        df['WODA POWROTNA KOLEKTORA KZ11']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ11'] +   
        df['WODA POWROTNA KOLEKTORA KZ12']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ12'] +   
        df['WODA POWROTNA KOLEKTORA KZ13']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ13'] +   
        df['WODA POWROTNA KOLEKTORA KZ15']*df['WODA CHŁODZĄCA DO KOLEKTOR KZ15'] 
    ) / df_tidy['woda_powrotna_przeplyw']
    df_tidy['woda_zasil_temp'] = (df['TEMP. WODY ZASIL.OBIEG PZ 1'] + df['TEMP. WODY ZASIL.OBIEG PZ 2'])/2
    df_tidy['koncentrat'] = df['REG NADAWY KONCENTRATU LIW1'] + df['REG NADAWY KONCENTRATU LIW2']
    df_tidy['pyl'] = df['REG PYL ZWROT LIW4']
    df_tidy['prazonka'] = df['REG KONCENTRAT PRAZONY LIW3']
    df_tidy['wymurowka_temp'] = df.iloc[:,22:46].apply('mean', axis = 1)
    df_tidy['prob_corg_masa'] = df['prob_corg'] * df_tidy['koncentrat']
    df_tidy['prob_s_masa'] = df['prob_s'] * df_tidy['koncentrat']
    df_tidy['prob_fe_masa'] = df['prob_fe'] * df_tidy['koncentrat']
    df_tidy['prazonka_fe_masa'] = df['Prażona mieszanina koncentratów HG1 - fe'] * df_tidy['prazonka']
    df_tidy['prazonka_s_masa'] = df['Prażona mieszanina koncentratów HG1 - sog'] * df_tidy['prazonka']
    df_tidy['wentylator'] = df.iloc[:,48:51].apply('mean', axis = 1)
    df_tidy['moc_cieplna_odebrana'] = df['SUMARYCZNA MOC CIEPLNA ODEBRANA - CAŁKOWITA']
    df_tidy['kol_kan_temp'] = df.iloc[:,46:48].apply('mean', axis = 1)
    
    
    req = pd.DataFrame({'colnames' : ['woda_powrotna_przeplyw', 'woda_powrotna_temp', 'woda_zasil_temp', 'koncentrat', 'pyl', 'prazonka', 'wymurowka_temp', 'prob_corg_masa', 'prob_s_masa', 'prob_fe_masa', 'prazonka_fe_masa', 'prazonka_s_masa', 'wentylator', 'moc_cieplna_odebrana', 'kol_kan_temp'],
        'window_end' : [0, 0, 0, 40, 50, 50, 0, 40, 40, 40, 0, 40, 0, 0, 50],
        'window_length' : [0, 4, 79, 4, 179, 179, 79, 4, 4, 4, 79, 4, 79, 79, 179]})
    
    df_final = pd.DataFrame()
    
    for temp_zuz_minutes in temp_zuz['czas'].dt.minute.unique():
        df_subfinal = pd.DataFrame(temp_zuz[temp_zuz['czas'].dt.minute == temp_zuz_minutes][['temp_zuz', 'czas']])
        df_subfinal['czas_cet'] = df_subfinal['czas']
        df_subfinal['czas'] = pd.to_datetime(df_subfinal['czas'] - pd.Timedelta(temp_zuz_minutes,'m'), utc = True)
        for i in range(1,16):
            df_temp = pd.DataFrame(df_tidy.iloc[:,[0,i]])
            df_temp['czas'] = pd.to_datetime(df_temp['czas'] - pd.Timedelta(temp_zuz_minutes,'m'))
            time_end = int(req[req['colnames'] == df_tidy.columns[i]].window_end)
            time_length = int(req[req['colnames'] == df_tidy.columns[i]].window_length)
            if time_length<60 :
                df_temp['czas_temp'] = df_temp['czas']+pd.Timedelta(time_end + time_length,'m')
                df_temp = pd.DataFrame(df_temp[df_temp['czas_temp'].dt.minute <=time_length])
                
                df_temp['czas'] = df_temp['czas_temp'].dt.floor('H', ambiguous = 'NaT')
                df_temp = df_temp.groupby('czas').mean().reset_index()
                df_temp['czas'] = pd.to_datetime(df_temp['czas'], utc = True)
                df_subfinal = pd.merge(df_subfinal, df_temp, on = 'czas', how = 'left')
            else:
                df_temp['czas_temp'] = df_temp['czas']+pd.Timedelta(time_end + time_length,'m')
                
                df_temp_temp = df_temp
                dummy_time = time_length - 60
                while dummy_time > 60:
                    df_temp['czas_temp'] = df_temp['czas_temp'] - pd.Timedelta(60, 'm')
                    df_temp_temp = pd.concat([df_temp_temp, df_temp], ignore_index=True)
                    dummy_time -= 60
                
                df_temp['czas_temp'] = df_temp['czas_temp'] - pd.Timedelta(60, 'm')
                df_temp_temp = pd.concat([df_temp_temp, pd.DataFrame(df_temp[df_temp['czas_temp'].dt.minute <=dummy_time])], ignore_index=True)
                df_temp_temp['czas'] = df_temp_temp['czas_temp'].dt.floor('H', ambiguous = 'NaT')
                df_temp = df_temp_temp.groupby('czas').mean().reset_index()
                df_temp['czas'] = pd.to_datetime(df_temp['czas'], utc= True)
                df_subfinal = pd.merge(df_subfinal, df_temp, on = 'czas', how = 'left')
        
        df_final = pd.concat([df_final, df_subfinal.drop('czas',axis=1)])
    df_final = df_final.sort_values('czas_cet')
    df_final = df_final.rename(columns={"czas_cet":"czas"})
    return df_final


data_folder = './data/zadanie-3-sztuczny-analizator-temperatury-żużla-wewnątrz-pieca-zawiesionowego/'

    
df = load_transform_df(data_folder)
print(df)