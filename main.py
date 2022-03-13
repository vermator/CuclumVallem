from predykcja import predykcja
from preprocessing danych import load_transform_df

data_folder = './data/zadanie-3-sztuczny-analizator-temperatury-żużla-wewnątrz-pieca-zawiesionowego/'
df = load_transform_df(data_folder)
print('Loaded and transformed')
y, r = predykcja(df)
print('Done')