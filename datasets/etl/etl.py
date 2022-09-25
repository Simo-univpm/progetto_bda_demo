import pandas as pd
import numpy as np
from os.path import dirname, abspath

def traduci_mese(mese):
    
    if mese == "gennaio": return "January"
    if mese == "febbraio": return "February"
    if mese == "marzo": return "March"
    if mese == "aprile": return "April"
    if mese == "maggio": return "May"
    if mese == "giugno": return "June"
    if mese == "luglio": return "July"
    if mese == "agosto": return "August"
    if mese == "settembre": return "September"
    if mese == "ottobre": return "October"
    if mese == "novembre": return "November"
    if mese == "dicembre": return "December"
    
    return mese


PATH = dirname(dirname(abspath(__file__)))
PATH = PATH.replace("\\", "/")


# ETL DATASETS DISPONIBILITA' (OK) =========================================================================================================================================
# IMPORTANTE: !!! RINOMINARE I NOMI DEI FILES E DELLE COLONNE IN BASE ALLE NECESSITA' (righe 30 - 36) !!!

df_1 = pd.read_excel(PATH + "/availability_dataset_2022-09-20_2022-09-22_booking.xlsx", index_col=0)
df_1["checkin"] = "2022-09-20"
df_1["checkout"] = "2022-09-22"

df_2 = pd.read_excel(PATH + "/availability_dataset_2022-09-22_2022-09-25_booking.xlsx", index_col=0)
df_2["checkin"] = "2022-09-22"
df_2["checkout"] = "2022-09-25"

# unisco i 2 dataframes in un unico dataframes ed effettuo operazioni di pulizia su di esso
frames = [df_1, df_2]
result = pd.concat(frames)

result.index.names = ['index']
result.drop(['url'], axis=1, inplace = True)
result = result[["id", "tipologia_stanza", "numero_persone", "prezzo_pieno", "prezzo_scontato", "checkin", "checkout"]]
result.rename(columns = {'tipologia_stanza':'room_type',
                         'numero_persone':'guest_number',
                         'prezzo_pieno':'full_price',
                         'prezzo_scontato':'discount_price',
                        }, inplace = True)

result.to_excel(PATH + "/etl/ETL_disponibilita.xlsx", header = True)
print(f'file [ETL_disponibilita.xlsx] scritto su [{PATH}/etl]')


# ETL DATASET DATI GENERALI (OK) =========================================================================================================================================
PATH = PATH +  f'/merged_datasets/'

df = pd.read_excel(PATH + "General_data_merged.xlsx", index_col=0)

df.index.names = ['index']
df = df[["id", "name_x", "name_y", "address_x", "address_y", "description", "host_description", "about", "facilities_x", "facilities_y", "price", "url_x", "url_y"]]
df['address_x'] = df['address_x'].fillna('none') # sostituzione valore mancante con 'None' per effettuare successivamente l'imputazione dei valori nel for


street_column = []
zip_code_column = []
city_column = []

# imputazione dei valori delle colonne di booking tramite i valori delle colonne di tripadvisor
for index, row in df.iterrows():
    if row["address_x"] == "none":
        row["address_x"] = row["address_y"]
        row["description"] = row["about"]
        row["facilities_x"] = row["facilities_y"]
        row["name_x"] = row["name_y"]
        row["host_description"] = "No camping host description"

for index, row in df.iterrows():
    street = row["address_x"].split(",", maxsplit = 1)[0] # prendo la via
    street_column.append(street)

    zip_code = row["address_x"].split(",", maxsplit = 1)[1][1:6] # prendo il cap
    zip_code_column.append(zip_code)

    city = row["address_x"].split(",", maxsplit = 1)[1][7:] # prendo la città
    city_column.append(city)


df["street"] = pd.Series(street_column)
df["zip_code"] = pd.Series(zip_code_column)
df["city"] = pd.Series(city_column)


df.rename(columns = {
                     'name_x': 'name',
                     'address_x':'address',
                     'facilities_x':'facilities'
                     }, inplace = True)


df.drop(['name_y', 'address_y', 'facilities_y', 'url_x', 'url_y'], axis=1, inplace = True)


PATH = dirname(dirname(abspath(__file__)))
PATH = PATH.replace("\\", "/")

df.to_excel(PATH + "/etl/ETL_strutture.xlsx", header = True)
print(f'file [ETL_strutture.xlsx] scritto su [{PATH}/etl]')


# ETL DATASET RECENSIONI (OK) =========================================================================================================================================

# colonne per il nuovo dataframe
id_column = []
vote_column = []
month_column = []
year_column = []
room_type_column = []
username_column = []
title_column = []
source_column = []
reviews_negative_column = []
reviews_positive_column = []
review_text_column = []


df = pd.read_excel(PATH + "/merged_datasets/Reviews_data_merged.xlsx", index_col=0)

# sostituzione valore mancante con 'none' per effettuare successivamente l'imputazione dei valori nel for
df['username'] = df['username'].fillna('none')

# etl recensioni booking
for index, row in df.iterrows():
    if row["username"] == "none":

        # salta l'iterazione corrente se la riga non contiene la data
        if row["review_staydate"] == "no date":
            year_column.append(np.nan)
            month_column.append(np.nan)
            continue


        # id
        id_column.append(row["id"])

        # voto
        # converte il voto da stringa a float
        if row["reviews_vote"] == "10":
            vote_column.append('%.1f' % float(10))
        else:
            voto = ""
            voto = voto + row["reviews_vote"][0]
            voto = voto + "."
            voto = voto + row["reviews_vote"][-1]
            vote_column.append('%.1f' % float(voto))


        # titolo
        title_column.append(row["reviews_title"])

        # recensione positiva
        reviews_positive_column.append(row["reviews_positive"])

        # recensione negativa
        reviews_negative_column.append(row["reviews_negative"])

        # reviews text
        review_text_column.append("none")

        # room type
        # rimuove il pallino dal roomtype
        room = ""
        room = row["room_type"][3:-1]
        #row["room_type"] = room
        room_type_column.append(room)

        # mese
        # traduce il mese del soggiorno in inglese e lo scrive nella colonna month
        row["review_staydate"] = row["review_staydate"].partition("di")[2]
        mese = row["review_staydate"].split()[0]
        month = traduci_mese(mese)
        month_column.append(month)

        # anno
        # scrive l'anno del soggiorno nella colonna year
        year = row["review_staydate"].split()[1]
        year_column.append(year)

        # source
        source_column.append("Booking")


# etl recensioni tripadvisor
for index, row in df.iterrows():
    if not row["username"] == "none":

        # salta l'iterazione corrente se la riga non contiene la data
        if row["stay_date"] == "no date":
            year_column.append(np.nan)
            month_column.append(np.nan)
            continue

        # id
        id_column.append(row["id"])

        # voto
        vote_column.append('%.1f' % float((row["rating"]/10)*2))

        # titolo
        title_column.append(row["title"])

        # recensione positiva
        reviews_positive_column.append("none")

        # recensione negativa
        reviews_negative_column.append("none")

        # reviews text
        review_text_column.append(row["review_text"])

        # room type
        room_type_column.append('none')

        # mese
        row["stay_date"] = row["stay_date"].partition(":")[2]
        mese = row["stay_date"].split()[0]
        month = traduci_mese(mese)
        month_column.append(month)

        # anno
        year = row["stay_date"].split()[1]
        year_column.append(year)

        # source
        source_column.append("Tripadvisor")

# creo dizionario con i nuovi dati
raw_reviews_data = {
                    'id': id_column,
                    'title': title_column,
                    'review_positive': reviews_positive_column,
                    'review_negative': reviews_negative_column,
                    'review_text': review_text_column,
                    'vote': vote_column,
                    'month': month_column,
                    'year': year_column,
                    'room_type': room_type_column,
                    'source': source_column
                    }

# creo dataframe dal dizionario
etl_reviews_data = pd.DataFrame(data = raw_reviews_data)

# scrivo su disco
etl_reviews_data.to_excel(PATH + "/etl/ETL_recensioni.xlsx", header = True)
print(f'file [ETL_recensioni.xlsx] scritto su [{PATH}/etl]')