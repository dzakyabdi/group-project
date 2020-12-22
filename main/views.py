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

model = None
# class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
#                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

class_names = ['beef tartare', 'chicken curry', 'chocolate mousse', 'french toast',
               'fried_rice', 'hot dog', 'ice cream', 'lasagna', 'oysters', 'pizza', 'takoyaki']

spoonacular_api = "https://api.spoonacular.com"


def index(request):
    global model
    global class_names
    response = {}
    json_file = open('model11.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = keras.models.model_from_json(loaded_model_json)
    model.load_weights("model11.h5")
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
    response = {"prediksi_title": name, "prediksi_image": image_name, "hasil_list": hasilJson}

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
