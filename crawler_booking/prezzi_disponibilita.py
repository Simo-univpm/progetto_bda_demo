import requests # libreria per generare richieste HTTP
from bs4 import BeautifulSoup as bs # libreria per scraping
import pandas as pd
from os.path import dirname, abspath
import sys
head = head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}


def getAllCampingLinks(checkin, checkout):

  url = "https://www.booking.com/searchresults.it.html?ss=Marche%2C+Italia&is_ski_area=&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&dest_id=905&dest_type=region&search_selected=true&nflt=ht_id%3D224%3Bht_id%3D214"
  resp = requests.get(url, headers = head)
  soup = bs(resp.text, 'lxml')

  unedited_links = soup.find_all("a", {"data-testid": "title-link"}, href = True)
  #unedited_links = unedited_links[:3] # prende i primi 3 camping per la demo

  urls = []
  for link in unedited_links:
    
    app_url =  link['href'].partition("?")[0]
    url = f'{app_url}?checkin={checkin};checkout={checkout};selected_currency=EUR'
    urls.append(url)

  return urls

def getId(url):
  # "https://www.booking.com/hotel/it/camping-tre-archi.it.html?checkin=2022-09-17;checkout=2022-09-24;selected_currency=EUR"
  id = url.partition(".it.html")[0] # prende tutto quello prima di .it.html dall'url
  id = id.partition("it/")[2] # prende tutto quello dopo di it/ dall'url

  return id

def getAvailabilities(url):

  response = requests.get(url, headers = head)
  soup = bs(response.text, 'lxml')


  availability = [] # lista che contiene tutte le disponibilità di un camping

  available_rooms = soup.find("div", {"id": "available_rooms"})
  hprt_table_column = available_rooms.find("div", {"class": "hprt-table-column"})

  #if hprt_table_column is None: return availability # se la tabella delle disponibiltà non esiste si interrompe
  if hprt_table_column is not None:

    # si cercano tutte le righe della tabella delle disponibilità e si itera per ciascuna riga  
    tbody = hprt_table_column.find('tbody')
    all_tr = tbody.find_all('tr')

    type_found = False # per continuare correttamente l'esecuzione quando viene trovato il tipo della stanza
    id = getId(url) # chiave primaria per effettuare le operazioni di join

    for row in all_tr: # ciclando si prendono tutti i dati rilevanti della tabella delle disponbilità di booking
      table_row = []

      if not type_found:
        room_type = row.find("span", {"class": "hprt-roomtype-icon-link"})
        if room_type is not None:
          room_type = room_type.text.strip()
          type_found = True
      
      n_guests = row.find("div", {"class": "hprt-occupancy-occupancy-info"})
      if n_guests is not None:
        n_guests = n_guests.text.strip()
        n_guests = [int(s) for s in n_guests.split() if s.isdigit()][0]

      discount_price = row.find("div", {"class": "bui-f-color-destructive js-strikethrough-price prco-inline-block-maker-helper bui-price-display__original"})
      if discount_price is not None: discount_price = discount_price.text.strip()

      full_price = row.find("span", {"class": "prco-valign-middle-helper"})
      if full_price is not None: full_price = full_price.text.strip()

      table_row.append(room_type); table_row.append(n_guests); table_row.append(discount_price); table_row.append(full_price); table_row.append(url); table_row.append(id)
      availability.append(table_row)

      if "hprt-table-last-row" in row['class']: type_found = False


  return availability

def writeAvailabilitiesToExcel(dataset, checkin, checkout):

  OUTPUT_PATH = dirname(dirname(abspath(__file__)))
  OUTPUT_PATH = OUTPUT_PATH + f'/datasets/availability_dataset_{checkin}_{checkout}_booking.xlsx'
  OUTPUT_PATH = OUTPUT_PATH.replace("\\", "/")
  
  df = pd.DataFrame(dataset, columns = ["tipologia_stanza", "numero_persone", "prezzo_pieno", "prezzo_scontato", "url", "id"])
  df.to_excel(OUTPUT_PATH)

  print(f'file[availability_dataset_{checkin}_{checkout}_booking.xlsx] scritto su [{OUTPUT_PATH}]')
  

def main(checkin, checkout):

  # prendo tutte le disponibilita dei vari camping
  all_campings_links = getAllCampingLinks(checkin, checkout)

  # le aggiungo ad una lista
  list_of_availabilities = []
  for url in all_campings_links:
    list_of_availabilities.append(getAvailabilities(url))
    print("scraping disponibilita': " + url)
  
  # riduco la dimensionalità di 1 per scriverla a db
  availabilities = []
  for list in list_of_availabilities: 
    for availability in list:
      availabilities.append(availability)

  # scrivo il dataset a db
  writeAvailabilitiesToExcel(availabilities, checkin, checkout)


#main("2022-10-17", "2022-10-24")
main(sys.argv[1], sys.argv[2])