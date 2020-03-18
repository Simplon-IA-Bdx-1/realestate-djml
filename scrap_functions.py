#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from bien_immo import Bien_immo 

def scrap(ref):
    r = requests.get(f"https://www.green-acres.fr{ref}", headers={'Accept-Language' : "fr-FR"})
    soup = BeautifulSoup(r.content, 'html.parser')

    bien_immo = Bien_immo(ref = ref)

    main_characteristics = soup.find(class_="item-content-part main-characteristics")

    characteristics = []
    main_characteristics_ul = main_characteristics.find_next('ul')
    for li in main_characteristics_ul.find_all('li'):
        for p in li.find_all("p"):
            characteristics.append(p.get_text().strip())

    informations = soup.find(class_="item-content-part price item-ecology")
    environment = []
    for p in informations.find_all("p"):
        environment.append(p.get_text().strip())

    emplacement = environment[-1].split(" ")

    # Ville (city)
    if len(emplacement) == 10:
        bien_immo.city = emplacement[5][:-1]
    if len(emplacement) == 11:
        bien_immo.city = emplacement[5]+" "+emplacement[6][:-1]

    # Département (county)
    if len(emplacement) == 10:
        bien_immo.county = emplacement[7]
    if len(emplacement) == 11:
        bien_immo.county = emplacement[8]
    
    # Région (district)
    bien_immo.district = emplacement[-1][:-2]
    
    for characteristic in characteristics:
    # Surface habitable (area_m2)
        if re.match("\d{1,} m² de surface habitable", characteristic):
            bien_immo.area_m2 = int(characteristic.split(" ")[0])
    # Surface terrain (ground_m2)       
        if re.match("\d+,?\d+? hectares de terrain", characteristic):
            bien_immo.ground_m2 = int(float(re.sub(",", ".", characteristic.split(" ")[0]))*10000)
        if re.match("\d{1,} m² de terrain", characteristic):
            bien_immo.ground_m2 = characteristic.split(" ")[0]
    # Nombre de pièces (nb_room)
        if re.match("\d{1,} pièces", characteristic):
            bien_immo.nb_room = int(characteristic.split(" ")[0])
    # Nombre de chambres (nb_bedroom)
        if re.match("\d{1,} chambres", characteristic):
            bien_immo.nb_bedroom = int(characteristic.split(" ")[0])
    # Piscine (pool : booléen)
        if re.match("Piscine", characteristic):
            bien_immo.pool = True
    # Cave (cellar : booléen)
        if re.match("Cave", characteristic):
            bien_immo.cellar = True
    # Parking/Garage (garage : booléen)
        if re.match(".* parking", characteristic):
            bien_immo.garage = True
    # Prix (output)
    output = informations.find("h2")
    output = output.find(class_="price").get_text()
    bien_immo.output = int(re.sub("[\s€]","", output))

    return bien_immo.__dict__

def get_refs(page):
    r = requests.get(f"https://www.green-acres.fr/fr/prog_show_properties-order-date_d-lg-fr-cn-fr-i-24-city_id-rg_aquitaine.html?p_n={page}")
    soup = BeautifulSoup(r.content, "html.parser")
    agc = soup.find(id="adverts-grid-container")
    refs = []
    for figure in agc.find_all("figure"):
        a = figure.find("a", href=True)
        refs.append(a['href'])
    return refs

def get_nb_pages():
    r = requests.get(f"https://www.green-acres.fr/fr/prog_show_properties-order-date_d-lg-fr-cn-fr-i-24-city_id-rg_aquitaine.html?p_n=1")
    soup = BeautifulSoup(r.content, "html.parser")
    nb_pages = soup.find(class_="alert-title").get_text().split(" ")
    nb_pages = (int(re.sub("\\xa0", "", nb_pages[3])) // 24) + 1
    return nb_pages