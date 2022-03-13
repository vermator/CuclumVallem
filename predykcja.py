import pandas as pd
import joblib

def predykcja(df):
    # funkcja zwraca dwa parametry: y_pred - predykcje wartości temperatury żużla i r2 - statystykę r-squared
    filename = 'finalized_model.sav'
    lr = joblib.load(filename)
    
    df['czas_utc'] = pd.to_datetime(df['czas_utc'])
    df.drop(df[df['koncentrat']==0].index, axis=0, inplace=True) # usunięcie wierszy z koncentratem=0
    # usuniecie zmiennych, ktore w regresji liniowej miały p_value>0.05
    df.drop(['prazonka','prob_fe_masa','koncentrat','prob_s_masa','wymurowka_temp'], axis=1, inplace=True) 
    df.dropna(inplace=True) 
    features = df.drop('temp_zuz',axis=1).diff()
    features['prev_temp_zuz'] = df['temp_zuz'].shift(1)
    features = features.iloc[1:,:]
    features['czas_utc'] = features['czas_utc'].dt.seconds/3600
    label = df['temp_zuz'].iloc[1:,]
    
    y_pred = lr.predict(features)
    r2 = lr.score(features, label)
    print('R^2 = %.2f ' % r2)
    return y_pred, r2
    
