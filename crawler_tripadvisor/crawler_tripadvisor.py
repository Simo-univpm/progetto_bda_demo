import requests
from bs4 import BeautifulSoup as bs
import math
import pandas as pd
from os.path import dirname, abspath


#NO SITI .COM, tripadvisor da le recensioni in inglese e ce ne sono solo tipo 2 o 3

url = [
       "https://www.tripadvisor.it/Hotel_Review-g2189383-d4923901-Reviews-Centro_Vacanze_Garden_River-Altidona_Province_of_Fermo_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g2140648-d3519310-Reviews-Camping_Lpre-Ostra_Province_of_Ancona_Marche.html",
       "https://www.tripadvisor.it/Hotel_Review-g608900-d4817085-Reviews-Camping_Reno-Sirolo_Province_of_Ancona_Marche.html",
       "https://www.tripadvisor.it/Hotel_Review-g1924689-d948494-Reviews-Natural_Village_Resort-Porto_Potenza_Picena_Potenza_Picena_Province_of_Macerata_Marche.html",
       "https://www.tripadvisor.it/Hotel_Review-g1582949-d2346767-Reviews-La_Risacca_Camping_Village_Formule_Hotel-Porto_Sant_Elpidio_Province_of_Fermo_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g1741825-d1891906-Reviews-Girasole_Eco_Family_Village-Marina_Palmense_Fermo_Province_of_Fermo_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g608900-d1146098-Reviews-Green_Garden_Camping_Village-Sirolo_Province_of_Ancona_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g194914-d2344934-Reviews-Camping_Blu_Fantasy-Senigallia_Province_of_Ancona_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g2026765-d7082655-Reviews-Camping_Village_Mar_y_Sierra-San_Costanzo_Province_of_Pesaro_and_Urbino_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g2136886-d21340843-Reviews-Amapolas_Villaggio_Camping-Mombaroccio_Province_of_Pesaro_and_Urbino_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g1025201-d677045-Reviews-Villaggio_Turistico_Residence_Mare-Fermo_Province_of_Fermo_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g194914-d3309922-Reviews-Camping_Villaggio_Cortina-Senigallia_Province_of_Ancona_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g194742-d21379810-Reviews-Poggio_Imperiale_Marche-Civitanova_Marche_Province_of_Macerata_Marche.html", 
       "https://www.tripadvisor.it/Hotel_Review-g23906399-d12336250-Reviews-Casale_Civetta-Borgo_della_Consolazione_Trecastelli_Province_of_Ancona_Marche.html"
      ]

def getId(url):
  if "g2189383-d4923901"   in url: return "centro-vacanze-garden-river"
  if "g2140648-d3519310"   in url: return "camping-lpre"
  if "g608900-d4817085"    in url: return "camping-reno"
  if "g1924689-d948494"    in url: return "natural-village-resort"
  if "g1582949-d2346767"   in url: return "la-risacca-camping-village"
  if "g1741825-d1891906"   in url: return "girasole-eco-family-village"
  if "g608900-d1146098"    in url: return "green-garden-camping-village"
  if "g194914-d2344934"    in url: return "camping-blu-fantasy"
  if "g2026765-d7082655"   in url: return "camping-village-mar-y-sierra"
  if "g2136886-d21340843"  in url: return "amapolas-villaggio-camping"
  if "g1025201-d677045"    in url: return "villaggio-turistico-residence-mare"
  if "g194914-d3309922"    in url: return "camping-villaggio-cortina"
  if "g194742-d21379810"   in url: return "poggio-imperiale-marche"
  if "g23906399-d12336250" in url: return "casale-civetta"

def getGeneralAndFacilities(url):

  print(">>> scraping: ", url)

  head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
  resp = requests.get(url, headers = head)
  soup = bs(resp.text, 'lxml')

  camping_general = []

  camping_name = soup.find("h1", {"id": "HEADING"})
  if camping_name is not None: camping_name = camping_name.text
  
  camping_address = soup.find("span", {"class": "map-pin-fill"}).next_sibling
  if camping_address is not None: camping_address = camping_address.text

  camping_about = soup.find("div", {"id": "ABOUT_TAB"})
  ui_columns = camping_about.find("div", {"class": "ui_columns"})
  camping_about = ui_columns.find("div", {"class": "ssr-init-26f"})

  if camping_about is not None: camping_about = camping_about.text

  # non resistente ai cambi di classe html
  camping_price = soup.find("div", {"class": "JPNOn b Wi"})
  if camping_price is not None: camping_price = camping_price.text
  else: camping_price = "non disponibile"

  lista_div_servizi = soup.find_all("div", {"data-test-target": "amenity_text"})

  servizi_app = []
  for div_servizio in lista_div_servizi:
    servizi_app.append(div_servizio.text.strip())
    servizi_app.append(", ")

  camping_facilities = ''.join(map(str, servizi_app))

  id = getId(url)

  camping_general.append(camping_name); camping_general.append(camping_address); camping_general.append(camping_about); camping_general.append(camping_price); camping_general.append(camping_facilities); camping_general.append(url); camping_general.append(id)
  return camping_general

def getNumReviews(url):
  head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
  response = requests.get(url, headers = head)
  soup = bs(response.text, 'lxml')

  num_reviews = soup.find("span", {"class": "ui_bubble_rating"}).next_sibling
  num_reviews = num_reviews.text.split()[0]
  num_reviews = num_reviews.replace(".", "") # rimuove il punto  --> 1.405 --> 1405 per booking.it
  num_reviews = num_reviews.replace(",", "") # rimuove la virgola--> 1,405 --> 1405 per booking.com

  print("> NUMERO RECENSIONI: " + num_reviews)

  return int(num_reviews)

def editLinksReviews(url):

  num_reviews = getNumReviews(url) # numero totale di recensioni per camping (5 per pagina)
  num_pag = int(math.ceil(int(num_reviews)/5)) # numero di pagine di recensione per camping

  print("> NUMERO DI PAGINE DI RECENSIONI: " + str(num_pag))

  pag_review = 0 # variabile per incrementare di 5 in 5 l'url della pagina delle recensioni
  edited_links_reviews = [] # lista per contenere tutti gli url delle recensioni di un sito di camping
  for i in range(num_pag):
    url_appoggio = url.replace("Reviews-", f'Reviews-or{pag_review}-')
    edited_links_reviews.append(url_appoggio)
    pag_review += 5

  return edited_links_reviews

def getReviewRating(tag):
  # estrapola il voto dal tag span della recensione
  rating_string = tag['class'][1]

  if rating_string == "bubble_10": return 10
  if rating_string == "bubble_20": return 20
  if rating_string == "bubble_30": return 30
  if rating_string == "bubble_40": return 40
  if rating_string == "bubble_50": return 50

  if rating_string is not "bubble_10" | "bubble_20" | "bubble_30" | "bubble_40" | "bubble_50": return "no rating"

def getReviews(url):

  # ritorna le 5 recensioni presenti nella pagina in una lista
  print(">>> scraping: ", url)

  head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
  response = requests.get(url, headers = head)
  soup = bs(response.text, 'lxml')


  lista_div_recensioni = soup.find_all("div", {"data-test-target": "HR_CC_CARD"})

  recensioni = []
  for div_recensioni in lista_div_recensioni:
    app_rec = []

    # utente che ha lasciato la recensione
    user = div_recensioni.find("a", {"class": "ui_header_link"}, href = True)
    if user is not None: app_rec.append(user.text)
    else: app_rec.append("no user")

    # voto della recensione
    rating = div_recensioni.find("span", {"class": "ui_bubble_rating"})
    if rating is not None: app_rec.append(getReviewRating(rating))
    else: app_rec.append("no rating")

    # titolo della recensione
    title = div_recensioni.find("div", {"data-test-target": "review-title"})
    if title is not None: app_rec.append(title.text)
    else: app_rec.append("no title")

    # corpo della recensione (sfrutto il titolo come punto di ancoraggio per evitare le classi dinamiche)
    review_text = title.next_sibling.contents[0].contents[0].text
    if review_text is not None: app_rec.append(review_text)
    else: app_rec.append("no text")

    # data della recensione
    # controllo se ogni elemento del div fratello del tag title contiene una stringa con scritto "Data del soggiorno"
    stay_date = ""
    match_1 = "Data del soggiorno"
    match_2 = "Date of stay"

    date_level = title.next_sibling
    length = len(title.next_sibling)
    
    for i in range(length):
      target = date_level.contents[i].contents[0].text
      if   match_1 in target: stay_date = target
      elif match_2 in target: stay_date = target

    if stay_date is not None: app_rec.append(stay_date)
    else: app_rec.append("no date")
    
    app_rec.append(url)
    app_rec.append(getId(url))

    recensioni.append(app_rec)
  
  return recensioni

def writeGeneralToExcel(dataset):

  OUTPUT_PATH = dirname(dirname(abspath(__file__)))
  OUTPUT_PATH = OUTPUT_PATH + f'/datasets/general_data_dataset_tripadvisor.xlsx'
  OUTPUT_PATH = OUTPUT_PATH.replace("\\", "/")
  
  columns = ["name", "address", "about", "price", "facilities", "url", "id"]
  df = pd.DataFrame(dataset, columns = columns)
  df.to_excel(OUTPUT_PATH)

  print(f'file [general_data_dataset_tripadvisor.xlsx] scritto su [{OUTPUT_PATH}]')
  
def writeReviewsToExcel(dataset):
  
  OUTPUT_PATH = dirname(dirname(abspath(__file__)))
  OUTPUT_PATH = OUTPUT_PATH + f'/datasets/review_dataset_tripadvisor.xlsx'
  OUTPUT_PATH = OUTPUT_PATH.replace("\\", "/")
  
  columns = ["username", "rating", "title", "review_text", "stay_date", "url", "id"]
  df = pd.DataFrame(dataset, columns = columns)
  df.to_excel(OUTPUT_PATH)

  print(f'file [review_dataset_tripadvisor.xlsx] scritto su [{OUTPUT_PATH}]')

def main(url):

  camping_general_data_and_facilities = [] # contiene dati generali e servizi di ogni singolo camping
  camping_reviews_links = [] # contiene tutti i link delle singole pagine di recensioni
  all_reviews = [] # contiene le singole recensioni di tutti i camping

  # SCRAPING DEI DATI GENERALI E SERVIZI ==============================================================
  for u in url: 
    camping_general_data_and_facilities.append(getGeneralAndFacilities(u)) 

  writeGeneralToExcel(camping_general_data_and_facilities)

  #SCRAPING DELLE RECENSIONI ==========================================================================
  # estrapolo tutti i link contenenti pagine di recensioni per ogni camping e li salvo in camping_reviews_links
  camping_reviews_links = map(editLinksReviews, url)

  # ciclo ogni link contenente le pagine di recensioni
  for list_of_links in camping_reviews_links:
    for link in list_of_links:

      # per ogni pagina di recensioni estraggo le singole recensioni e le salvo in all_reviews
      page_of_reviews = getReviews(link)
      for review in page_of_reviews:
        all_reviews.append(review)
  
  writeReviewsToExcel(all_reviews) # salvo le recensioni su file

main(url)