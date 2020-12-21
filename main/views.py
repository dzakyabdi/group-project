import matplotlib
import numpy as np
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

class_names = ['beef_tartare', 'chicken_curry', 'chocolate_mousse', 'french_toast',
               'fried_rice', 'hot_dog', 'ice_cream', 'lasagna', 'oysters', 'pizza', 'takoyaki']

tokopedia = "https://www.tokopedia.com/search?st=product&q="
bukalapak = "https://www.bukalapak.com/products?search%5Bkeywords%5D="
shopee = "https://shopee.co.id/search?keyword="


def index(request):
    global model
    global class_names
    response = {}
    # json_file = open('model.json', 'r')
    json_file = open('model11.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = keras.models.model_from_json(loaded_model_json)
    # model.load_weights("model.h5")
    model.load_weights("model11.h5")
    # model = keras.models.load_model("trainedmodel_11class.hdf5", compile=False)
    # model_best = load_model('bestmodel_3class.hdf5', compile=False)
    return render(request, 'index.html', response)


def result(request):
    image_name = handle_image(request.FILES.get('img'))
    # pred = real_prediction(request.FILES.get('img'))
    pred = predict_real(image_name)
    # plot_value_test(pred)
    maximum = np.max(pred[0])
    max_index = np.where(pred[0] == maximum)
    max_index = max_index[0][0]
    name = class_names[max_index]
    tokopedia_result = tokopedia + name
    bukalapak_result = bukalapak + name
    shopee_result = shopee + name
    response = {"prediksi_title": name, "prediksi_image": image_name, "tokopedia_url": tokopedia_result,
                "bukalapak_url": bukalapak_result, "shopee_url": shopee_result}
    return render(request, 'result.html', response)


def handle_image(f):
    print(settings.STATICFILES_DIRS[0])
    destination = open(settings.STATICFILES_DIRS[0] + '/image.png', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return f.name


# def real_prediction(image_name):
#     global model
#     global class_names
#     img = image.load_img(image_name, target_size=(28, 28))
#     img = image.img_to_array(img)
#     img = 255 - img
#     img_gray = np.mean(img, axis=2)
#     img_gray = img_gray/255.0
#
#     img_gray_exp = (np.expand_dims(img_gray,0))
#     pred = model.predict(img_gray_exp)
#
#     return pred


def predict_real(img_name):
    img = image.load_img(settings.STATICFILES_DIRS[0] + '/image.png', target_size=(299, 299))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    pred = model.predict(img)
    return pred


def plot_value_test(predictions_array):
    global model
    global class_names

    fig = plt.figure(num=None, figsize=(15, 8), dpi=150, facecolor='w', edgecolor='k')
    plt.grid(False)
    # plt.xticks(range(10))
    plt.xticks(range(45))
    plt.yticks([])
    # thisplot = plt.bar(range(10), predictions_array, color="#777777")
    thisplot = plt.bar(range(45), predictions_array[0], color="#777777")
    plt.ylim([0, 1])
    # predicted_label = np.argmax(predictions_array)
    predicted_label = np.argmax(predictions_array[0])
    thisplot[predicted_label].set_color('blue')
    plt.xlabel("Prediction percentage")

    fig.savefig(settings.STATICFILES_DIRS[0] + '/' + 'plot.png')
