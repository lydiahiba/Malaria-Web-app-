from __future__ import division, print_function
from flask import Flask,abort,render_template,request,redirect,url_for
#from werkzeug import secure_filename
#from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename

# coding=utf-8
import sys
import os
import glob
import re
import numpy as np

import zipfile

# Keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, flash
#from gevent.wsgi import WSGIServer
from gevent.pywsgi import WSGIServer
import os
#import magic
import urllib.request
from flask import Flask, flash, request, redirect, render_template



from flask import Flask

UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024




ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Model saved with Keras model.save()
MODEL_PATH = 'models/my_model.h5'

#Load your trained model
model = load_model(MODEL_PATH)
# model._make_predict_function()          # Necessary to make everything ready to run on the GPU ahead of time
print('Model loaded. Start serving...')


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(50,50)) #target_size must agree with what the trained model expects!!

    # Preprocessing the image
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0) # pour reshaper l'image de façon a qu'en aille 4 dimension (nombre d'image,size , size , channel color)

   
    preds = model.predict(img)
    pred = np.argmax(preds,axis = 1)
    return pred

def write_fichier(b):
    fichier = open("test.txt", "a")
    fichier.write(str(b)+ '\n')
    fichier.close()

def cellule_contaminee(file):
    f = open(file)
    cellule_cont = 0
    count = 0
    for line in f:
        count += 1
        if "[0]" in line:
            cellule_cont += 1
    f.close()
    st1 = 'le patient a la malaria'
    st2 = 'le patient est en bonne santé'
    if (((100*cellule_cont)/count) < 99.92):
        return st1
    else:
        return st2 
    
    
@app.route('/')
def upload_form():
    return render_template('upload.html')



@app.route('/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for f in request.files.getlist('files[]'):
            basepath = os.path.dirname(__file__)
            file_path = os.path.join(
                basepath, 'uploads', secure_filename(f.filename))
            f.save(file_path)
            flash('File(s) successfully uploaded') # ça permet d'afficher que le fichier a été uploader succcessfuly on trouve le code html dans le upload.html et pour la doc afin de comprendre ça : https://flask.palletsprojects.com/en/0.12.x/patterns/flashing/
            pred = model_predict(file_path, model)
            str1 = 'Malaria Parasitized'
            str2 = 'Normal'
            results = " "
            if pred == 0:
                results = str1
                write_fichier(pred)
            else:
                results = str2
                write_fichier(pred)

    return cellule_contaminee("test.txt")


if __name__ == "__main__":
    app.run(debug=True)