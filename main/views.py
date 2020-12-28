import matplotlib
import requests
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from tensorflow import keras

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from keras.preprocessing import image
from image_classification import settings
from tensorflow.keras.applications.inception_v3 import preprocess_input

import requests
from bs4 import BeautifulSoup
import json

all_cookies = dict()
headers = dict()
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
restaurants = [["" for x in range(4)] for y in range(20)] 

model = None
# class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
#                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# class_names = ['beef tartare', 'chicken curry', 'chocolate mousse', 'french toast',
#                'fried_rice', 'hot dog', 'ice cream', 'lasagna', 'oysters', 'Pizza', 'takoyaki']
class_names = ['Deviled Eggs', 'Caesar Salad','Lasagna','Tuna Tartare','Chicken Curry','Beef Carpaccio','Ceviche', 'Hot And Sour Soup',
 'Steak','Shrimp And Grits','Risotto','Spaghetti Bolognese','Guacamole','French Fries','Beignets','Macaroni And Cheese','Nachos',
 'Grilled Salmon','French Toast','Fried Rice','Fish And Chips','Hummus','Donuts','Ramen','Tacos','Chocolate Mousse','Falafel','Prime Rib',
 'Lobster Roll Sandwich','Peking Duck','Beef Tartare','Foie Gras','Sashimi','Waffles','Lobster Bisque','Grilled Cheese Sandwich','Fried Calamari',
 'Crab Cakes','Clam Chowder','Pancakes','Oysters','Bread Pudding','Chocolate Cake', 'Carrot Cake','Club Sandwich','Eggs Benedict',
 'Ice Cream','Apple Pie','Beet Salad','Baklava','Garlic Bread','Frozen Yogurt','Onion Rings','Omelette','Greek Salad','Seaweed Salad',
 'Samosa','Cup Cakes','Breakfast Burrito','Tiramisu','Pork Chop','Cannoli','Red Velvet Cake','Baby Back Ribs','Takoyaki','Hot Dog',
 'Scallops','Spring Rolls', 'Edamame','Pho','Pad Thai','Spaghetti Carbonara','Caprese Salad','Poutine','Churros','Chicken Wings','Bruschetta',
 'Paella','Cheesecake','Filet Mignon','Dumplings','Croque Madame','Creme Brulee''Macarons','Strawberry Shortcake','Panna Cotta',
 'Hamburger','Bibimbap','French Onion Soup','Gyoza','Pizza','Cheese Plate','Ravioli','Mussels', 'Chicken Quesadilla','Escargots','Gnocchi',
 'Pulled Pork Sandwich','Miso Soup','Huevos Rancheros','Sushi']
class_names.sort()


spoonacular_api = "https://api.spoonacular.com"


def index(request):
    global model
    global class_names
    response = {}
    json_file = open('model101.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = keras.models.model_from_json(loaded_model_json)
    model.load_weights("model101.h5")
    return render(request, 'index.html', response)


def result(request):
    image_name = handle_image(request.FILES.get('img'))
    pred = predict_real(image_name)
    maximum = np.max(pred[0])
    max_index = np.where(pred[0] == maximum)
    max_index = max_index[0][0]
    name = class_names[max_index]
    jsonSpoonacular = requests.get(spoonacular_api + '/recipes/complexSearch?instructionsRequired=true&addRecipeInformation=true&apiKey=6a3ef2a911e74c659aee8978aa91e7dc&query=' + name)
    hasilJson = jsonSpoonacular.json()
    for i in range(1,3):
        list_restaurants = scrape_restaurants(name, i)
    response = {"prediksi_title": name, "prediksi_image": image_name, "hasil_list": hasilJson, "restaurants": list_restaurants[0:-5]}

    return render(request, 'result.html', response)


def recipe_detail(request, nama, index):
    jsonSpoonacular = requests.get(spoonacular_api + '/recipes/complexSearch?instructionsRequired=true&addRecipeInformation=true&apiKey=6a3ef2a911e74c659aee8978aa91e7dc&query=' + nama)
    hasilJson = jsonSpoonacular.json()
    for num, hasil in enumerate(hasilJson['results']):
        if num == index:
            hasilAkhir = hasil
            for hasil_resep in hasilAkhir["analyzedInstructions"]:
                    resep = hasil_resep['steps']

    response = { "hasil": hasilAkhir, "resep" : resep}

    return render(request, 'recipe_detail.html', response)

def handle_image(f):
    print(settings.STATICFILES_DIRS[0])
    destination = open(settings.STATICFILES_DIRS[0] + '/image.png', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return f.name


def predict_real(img_name):
    img = image.load_img(settings.STATICFILES_DIRS[0] + '/image.png', target_size=(299, 299))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    pred = model.predict(img)
    return pred

def get_cookies():
    global all_cookies

    f = open("cookies.json","r")
    cookiedata = f.read()
    f.close()

    cookiedata = json.loads(cookiedata)

    for i in cookiedata:
        name = i["name"]
        value = i["value"]
        all_cookies[name] = value

def connect_zomato():
    r = requests.get("https://zomato.com", cookies=all_cookies, headers=headers)
    if("Log out" in r.text):
        print("Logged in!")
    else:
        print("Invalid cookies")

def scrape_restaurants(dish, pg_no):
    r = requests.get("https://www.zomato.com/id/jakarta/kemang-restoran?q=%s&page=%d"%(dish,pg_no), headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.find_all("div",{'class':'search-snippet-card'})
    i = 0
    for div in divs:
        res_name = div.findChildren("a",{'class':'result-title'})
        res_rating = div.findChildren("span",{'class':'rating-value'})
        res_address = div.findChildren("div",{'class':'search-result-address'})
        res_price = div.find_all("div",{'class':'search-page-text'})
        for a in res_name:
            name = a.text
            restaurants[i][0] = name
        for a in res_rating:
            rating = a.text
            restaurants[i][1] = str(rating)
        for a in res_address:
            address = a.text
            restaurants[i][2] = address
        for price in res_price:
            res_price_children = price.findChildren("div",{'class':'res-cost'})
            for a in res_price_children:
                the_real_price = a.findChildren("span",{'class':'col-s-11'})
                for b in the_real_price:
                    price = b.text
                    restaurants[i][3] = str(price)
        i = i+1
    return restaurants
