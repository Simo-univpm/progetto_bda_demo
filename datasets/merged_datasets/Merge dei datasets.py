# Merge dei datasets

import numpy as np
import pandas as pd
from os.path import dirname, abspath

PATH = dirname(dirname(abspath(__file__)))
PATH = PATH + f'/'
PATH = PATH.replace("\\", "/")

# merge datasets dati generali
general_booking_df = pd.read_excel(PATH + "general_data_dataset_booking.xlsx", index_col=0)
general_tripadvisor_df = pd.read_excel(PATH + "general_data_dataset_tripadvisor.xlsx", index_col=0)

camping_general_dataset = pd.merge(general_booking_df, general_tripadvisor_df, on = 'id', how='outer')
camping_general_dataset.to_excel(PATH + "/merged_datasets/General_data_merged.xlsx", header = True)
print(f'file [General_data_merged.xlsx] scritto su [{PATH}merged_datasets]')

# merge datasets recensioni
reviews_booking_ds = pd.read_excel(PATH + "review_dataset_booking.xlsx", index_col=0)
reviews_tripadvisor_ds = pd.read_excel(PATH + "review_dataset_tripadvisor.xlsx", index_col=0)


#reviews_merged_df = pd.merge(reviews_booking_ds, reviews_tripadvisor_ds, on = 'id', how='outer')
#reviews_merged_df.to_excel(PATH + "/merged_datasets/Reviews_data_merged.xlsx", header = True)
#print(f'file [Reviews_data_merged.xlsx] scritto su [{PATH}merged_datasets]')

reviews_vote_column = []
reviews_title_column = []
room_type_column = []
reviews_negative_column = []
reviews_positive_column = []
review_staydate_column = []
url_x_column = []
id_column = []
username_column = []
rating_column = []
title_column = []
review_text_column = []
stay_date_column = []
url_y_column = []

for index, row in reviews_booking_ds.iterrows():

    if row["review_staydate"] == "no stay_date": continue

    reviews_vote_column.append(row["reviews_vote"])
    reviews_title_column.append(row["reviews_title"])
    room_type_column.append(row["room_type"])
    reviews_negative_column.append(row["reviews_negative"])
    reviews_positive_column.append(row["reviews_positive"])
    review_staydate_column.append(row["review_staydate"])
    url_x_column.append(row["url"])
    id_column.append(row["id"])
    username_column.append("none")
    rating_column.append("none")
    title_column.append("none")
    review_text_column.append("none")
    stay_date_column.append("none")
    url_y_column.append("none")

for index, row in reviews_tripadvisor_ds.iterrows():

    if pd.isnull(row["stay_date"]): continue

    reviews_vote_column.append("none")
    reviews_title_column.append("none")
    room_type_column.append("none")
    reviews_negative_column.append("none")
    reviews_positive_column.append("none")
    review_staydate_column.append("none")
    url_x_column.append("none")
    id_column.append(row["id"])
    username_column.append(row["username"])
    rating_column.append(row["rating"])
    title_column.append(row["title"])
    review_text_column.append(row["review_text"])
    stay_date_column.append(row["stay_date"])
    url_y_column.append(row["url"])

# creo dizionario con i nuovi dati
reviews_data_merged_dictionary = {
    'reviews_vote': reviews_vote_column,
    'reviews_title': reviews_title_column,
    'room_type': room_type_column,
    'reviews_negative': reviews_negative_column,
    'reviews_positive': reviews_positive_column,
    'review_staydate': review_staydate_column,
    'url_x': url_x_column,
    'id': id_column,
    'username': username_column,
    'rating': rating_column,
    'title': title_column,
    'review_text': review_text_column,
    'stay_date': stay_date_column,
    'url_y': url_y_column
    }

# creo dataframe dal dizionario
reviews_merged_df = pd.DataFrame(data = reviews_data_merged_dictionary)

# scrivo su disco
reviews_merged_df.to_excel(PATH + "/merged_datasets/Reviews_data_merged.xlsx", header = True)
print(f'file [Reviews_data_merged.xlsx] scritto su [{PATH}merged_datasets]')