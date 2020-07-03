from flask import Flask,render_template,url_for,request
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

import pandas as pd 
import numpy as np
import pickle
import sys
import nltk
import requests

import os
import sys
import requests
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

from functions import *

os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'] = '1b918f91d69241449f285ee7fed397db'
os.environ['COMPUTER_VISION_ENDPOINT'] = 'https://westcentralus.api.cognitive.microsoft.com/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

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
    # IMAGE_SIZE = (12, 8)
# @app.route('/')
# def home():
    image_path = TEST_IMAGE_PATHS[0]
    print(image_path)
    text_dict = get_actual_lines(get_image_ocr(image_path=image_path))
    invoice_dict = get_region(text_dict=text_dict,keyword_list=['amount','total','amount (in usd)'],reverse_keyword_method=True)
    print(invoice_dict)
    ## if it doesnt give results try changing reverse_keyword_method to False
    data_list = get_data(text_dict=text_dict, region_dict=invoice_dict,is_numeric_data=True)
    print(data_list)

    invoice_final_data = calc_total_and_tax(data_list)

    qty_dict = get_region(text_dict=text_dict,keyword_list=['qty', 'quantity'],reverse_keyword_method=True)

    qty_list = get_data(text_dict=text_dict, region_dict=qty_dict)
    
    qty_list = [i for i in qty_list if i!=None]

    print(qty_list)

    description_dict = get_region(text_dict=text_dict,keyword_list=['units','item','items','description','item & decription','item description','services'],reverse_keyword_method=True)

    product_list_description = get_data(text_dict=text_dict, region_dict=description_dict,is_numeric_data=False)
    print(product_list_description)
    
    vendor_name = " ".join(list([check(i+ ' is random') for i in list(text_dict[0].values())][0]['NNP']))
    
    print(vendor_name)
    currencies_in_consideration = ['Dollar ($)',"Euro (\u20ac)","Rupees (\u20B9)"]

    dollar_count = []
    euro_count = []
    ruppes_count = []

    for value in list(text_dict.values()):
        for next_layer in list(value.values()):
            if '$' in next_layer:
    #             print('Dollar currency')
                dollar_count.append('$')
                
            elif u"\u20ac" in next_layer:
    #             print('Euro currency')
                euro_count.append(u'\u20ac')
                
            elif u"\u20B9" in next_layer or "Rs." in next_layer or "rupees" in next_layer.lower():
    #             print("Indian Rupees Currency")
                ruppes_count.append(u"\u20B9")
        
    invoice_currency = currencies_in_consideration[np.argmax([len(dollar_count),len(euro_count),len(ruppes_count)])]
    
    print([len(dollar_count),len(euro_count),len(ruppes_count)])

    df = pd.DataFrame()

    df.loc[0,'Vendor Name'] = vendor_name
    df.loc[0,'Invoice Currency'] = invoice_currency
    df.loc[0,'Actual Amount'] = invoice_final_data['actual_total']
    df.loc[0,'Final Amount'] = invoice_final_data['final_total']
    df.loc[0,'Taxes'] = np.nan
    df.loc[0,'Extra/ Discounts'] = np.nan
    if invoice_final_data['tax_and_extra']>0:
        df.loc[0,'Taxes'] = invoice_final_data['tax_and_extra']
    else:
        df.loc[0,'Extra/ Discounts'] = (-1)*invoice_final_data['tax_and_extra']

    df.loc[0,'Product List'] = str(product_list_description)
    df.loc[0,'Respective Quantity List'] = str(qty_list)
    
    return render_template('result_dataframe.html',tables=[df.to_html(classes='data')],titles = ['Invoice data'])


# @app.route('/predict',methods=['POST'])
# def predict():
#     return render_template('result_dataframe.html',tables=[df.to_html(classes='data')],titles = ['Invoice data'])
        

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
