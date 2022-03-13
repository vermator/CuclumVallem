# CuValleyHack
## Uruchom aby użyć finalnego modelu
Uruchom **main.py** żeby otrzymać predykcję i r-squared modelu - należy wpisać ścieżkę do folderu (już rozpakowanego) z danymi (obecnie jest tam ścieżka do danych z 3 dnich) do zmiennej **data_folder**.

## Opis plików/folderów
### Skrypty do analizy

**Code.ipynb** - skrypt wczytujący dane, wykonujący prepocessing danych a także przygotowujący dane do modelu

**models.ipynb** - skrypt testujący modele

**data** - folder, gdzie trzymane są dane

**output** - folder, gdzie znajdują sie wszystkie outputy

**finalized_model.sav** - finalny model (regresja liniowa)

### Finalne skrypty do wczytania i użycia modelu

**preprocessing_danych.py** - funkcja pobierająca dane, preprocesująca dane i przygotowująca data frame do skryptu predykcja.py (inputem jest ścieżka do folderu z danymi) 

**predykcja.py** - funkcja biorąca przygotowanego data frama i robiąca predykcję (inputem jest data frame ze skryptu  preprocessing_danych)

**main.py** - finalny skrypt do użycia finalnego modelu

## Biblioteki
Potrzebne biblioteki do wykonania main.py: 
- numpy 
- pandas
- seaborn
- matplotlib.pyplot
- os
- openpyxl
- joblib

Inne potrzebne biblioteki (do Code.ipynb i models.ipynb):
- IPython.display
- sklearn
- statsmodels.api
