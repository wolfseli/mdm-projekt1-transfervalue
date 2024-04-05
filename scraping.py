# import libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ----------------- Scraping Fbref -----------------

# fbref table link
url_df = 'https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats'
# Header hinzufügen um 403 Fehler zu vermeiden
headers = {'User-Agent': 'Mozilla/5.0'}
df_fb = pd.read_html(requests.get(url_df).text.replace('<!--','').replace('-->',''))
print(df_fb)

# ----------------- Cleaning Fbref -----------------

# zweite Tabelle auswählen
df_second_table = df_fb[1]

# Header löschen
df_second_table.columns = df_second_table.columns.droplevel()

# erste Zeile löschen
df_second_table = df_second_table.drop(df_second_table.columns[0], axis=1)

# Spaltennamen anzeigen
print(df_second_table.columns)

# letze Spalte löschen
df_second_table = df_second_table.drop(df_second_table.columns[-1], axis=1)

# doppelte Spalten löschen
df_third_table_witout_doubles = df_second_table.loc[:, ~df_second_table.columns.duplicated()]
df_second_table = df_third_table_witout_doubles

# Spaltennamen anzeigen
print(df_second_table.columns)

# In Spalte "Age" alles nach den ersten 2 Zeichen löschen
df_second_table['Age'] = df_second_table['Age'].str[:2]

# Spalte mit namen "Nation", "Squad", "Born", "G+A-PK" und "xG+xAG" löschen
df_second_table = df_second_table.drop('Nation', axis=1)
df_second_table = df_second_table.drop('Squad', axis=1)
df_second_table = df_second_table.drop('G+A-PK', axis=1)
df_second_table = df_second_table.drop('xG+xAG', axis=1)
df_second_table = df_second_table.drop('Born', axis=1)

# Nur Zeilen behalten die in der Spalte "Pos" den Wert "FW" "MF,FW" oder "FW,MF" haben
df_second_table = df_second_table[df_second_table['Pos'].isin(['FW', 'MF,FW', 'FW,MF',])]

# Spalte "Pos" löschen
df_second_table = df_second_table.drop('Pos', axis=1)

# Anzeigen der zweiten Tabelle
print(df_second_table)

# Zeilen die mit "Player" beginnen löschen
df_second_table = df_second_table[~df_second_table['Player'].str.contains('Player')]

# Spalte "Comp" bereinigen
df_second_table['Comp'] = df_second_table['Comp'].str.split(' ').str[0]

# Anzeigen der Tabelle
print(df_second_table)

# ----------------- Scraping Transfermarkt -----------------

PlayersList = []
ValuesList = []

# Alle Wettbewerbe durchgehen / GB1 = Premier League /IT1 = Serie A / L1 = Bundesliga / ES1 = La Liga / FR1 = Ligue 1
for comp in ['GB1', 'IT1', 'ES1', 'L1', 'FR1']:

    # Alle 4 Seiten durchgehen
    for i in range(1, 4):
        url_tm = 'https://www.transfermarkt.de/premier-league/marktwerte/wettbewerb/'+ comp +'/pos/Sturm/detailpos/0/altersklasse/alle/plus/1/galerie/0/page/' + str(i)
        page = requests.get(url_tm, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        # players und values finden
        players = soup.find_all('img', {"class": 'bilderrahmen-fixed lazy lazy'})
        values = soup.find_all('td', class_='rechts hauptlink')

        # clean data
        for i in range(0, len(players)):
            PlayersList.append(players[i].get('alt'))

        for i in range(0, len(values)):
            ValuesList.append(values[i].text)

# DataFrame erstellen
df_tf = pd.DataFrame(list(zip(PlayersList, ValuesList)), columns=['Player', 'Value'])


# Anzeigen des gesamten DataFrames
print(df_tf)

# ----------------- Cleaning Transfermarkt -----------------

# Werte in der Spalte "Value" bereinigen
df_tf['Value'] = df_tf['Value'].str.replace('€', '')
df_tf['Value'] = df_tf['Value'].str.replace('Mio.', '0000')
df_tf['Value'] = df_tf['Value'].str.replace('Tsd.', '000')
df_tf['Value'] = df_tf['Value'].str.replace(' ', '')
df_tf['Value'] = df_tf['Value'].str.replace(',', '')

# Alle Sonderzeichen bei Namen in der Spalte "Player" umwandeln in die nächstliegende ASCII-Entsprechung bei beiden DataFrames
df_second_table['Player'] = df_second_table['Player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df_tf['Player'] = df_tf['Player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Anzeigen des DataFrames
print(df_tf)

# ----------------- Merging DataFrames -----------------

# merge dataframes
df_merged = pd.merge(df_second_table, df_tf, on='Player', how='left')

# NaN Werte mit 0 ersetzen
df_merged = df_merged.fillna(0)

# Zeilen mit Value 0 löschen
df_merged = df_merged[df_merged['Value'] != 0]

# Doubletten löschen
df_merged = df_merged.drop_duplicates(subset='Player')

# Spalte "Player" löschen
df_merged = df_merged.drop('Player', axis=1)

# Werte in Integer und Float umwandeln
df_merged['Value'] = df_merged['Value'].astype(int)
df_merged['MP'] = df_merged['MP'].astype(int)
df_merged['Starts'] = df_merged['Starts'].astype(int)
df_merged['Min'] = df_merged['Min'].astype(int)
df_merged['Gls'] = df_merged['Gls'].astype(int)
df_merged['Ast'] = df_merged['Ast'].astype(int)
df_merged['PK'] = df_merged['PK'].astype(int)
df_merged['PKatt'] = df_merged['PKatt'].astype(int)
df_merged['CrdY'] = df_merged['CrdY'].astype(int)
df_merged['CrdR'] = df_merged['CrdR'].astype(int)
df_merged['xG'] = df_merged['xG'].astype(float)
df_merged['npxG'] = df_merged['npxG'].astype(float)
df_merged['xAG'] = df_merged['xAG'].astype(float)
df_merged['npxG+xAG'] = df_merged['npxG+xAG'].astype(float)
df_merged['PrgC'] = df_merged['PrgC'].astype(int)
df_merged['PrgP'] = df_merged['PrgP'].astype(int)
df_merged['PrgR'] = df_merged['PrgR'].astype(int)
df_merged['G-PK'] = df_merged['G-PK'].astype(int)
df_merged['Age'] = df_merged['Age'].astype(int)
df_merged['90s'] = df_merged['90s'].astype(float)
df_merged['G+A'] = df_merged['G+A'].astype(int)

# Saplte "Comp" in kategorischen Wert umwandeln / One-Hot-Encoding
df_merged = pd.get_dummies(df_merged, columns=['Comp'])

# Anzeigen des DataFrames
print(df_merged)

# ----------------- Export DataFrames -----------------

# Dataframe jsonl format speichern und Datei im ordner "downloads" speichern
df_merged.to_json('downloads/file.jl', orient='records', lines=True)