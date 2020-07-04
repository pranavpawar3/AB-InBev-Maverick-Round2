from flask import Flask,render_template,url_for,request
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

import pandas as pd 
import numpy as np
import pickle

import os
import sys
import requests
import time
import logging

logging.getLogger().setLevel(logging.INFO)

from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# data = {"username": "pranavpawar3@gmail.com", "password": "Googleyash46"}
data = {"username": "pipodab832@kartk5.com", "password": "dataBrewers1"}
auth_token = requests.post('https://api.elis.rossum.ai/v1/auth/login',data=data).json()['key']

que_url = requests.get('https://api.elis.rossum.ai/v1/queues?page_size=1',
            headers={'Authorization': f'Token {auth_token}'}).json()['results'][0]['url']

que_id = que_url.split('/')[-1]

logging.info('credentials loaded!')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['pdf','png', 'jpg', 'jpeg'])

@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2) ]

    image_path = TEST_IMAGE_PATHS[0]
    filepath = image_path

    queue_id = que_id #47431
    username = "pipodab832@kartk5.com"
    password = "dataBrewers1"
    endpoint = 'https://api.elis.rossum.ai/v1'
    path = filepath

    url = "https://api.elis.rossum.ai/v1/queues/%s/upload" % queue_id
    with open(path, "rb") as f:
            response = requests.post(
                url,
                files={"content": f},
                auth=(username, password),
            )
    annotation_url = response.json()["results"][0]["annotation"]
    doc_id = annotation_url.split('/')[-1]

    logging.info("The file is reachable at the following URL:{}, and this id {}".format(annotation_url,doc_id))

    ## lets give it some time to process
    time.sleep(5)

    okay=True
    while okay:
        if requests.get('{}'.format(annotation_url),
                headers={'Authorization': f'Token {auth_token}'}).json()['status'] == 'to_review':
            logging.info('File Processed!! Lets checkout the results...')
            okay=False
        else:
            logging.info('not ready yet! might take a minute to process...')
            time.sleep(40)
            
    response = requests.get('{}/export?status=to_review&format=csv&id={}'.format(que_url,doc_id),
                headers={'Authorization': f'Token {auth_token}'})
    
    path = "../csv_outputs/{}_outputs.csv".format(filepath.split('/')[-1].strip('.pdf'))
    f = open(path, "wb")
    # writer = csv.writer(f)
    # writer.writerows(str(response.content).split('\\n'))
    f.write(response.content)
    f.close()


    df = pd.read_csv(path)

    primary_df = df.loc[:,:'Notes'].drop_duplicates().T

    item_df = df.loc[:,'Description':]
    
    return render_template('result_dataframe.html',tables=[primary_df.to_html(classes='data'),item_df.to_html(classes='data')],titles = ['Invoice data'])


# @app.route('/predict',methods=['POST'])
# def predict():
#     return render_template('result_dataframe.html',tables=[df.to_html(classes='data')],titles = ['Invoice data'])
        

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=2000, debug=True)
