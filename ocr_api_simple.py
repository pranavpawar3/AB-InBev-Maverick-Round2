from flask import Flask,render_template,url_for,request
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

from functions import *

os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'] = '1b918f91d69241449f285ee7fed397db'
os.environ['COMPUTER_VISION_ENDPOINT'] = 'https://westcentralus.api.cognitive.microsoft.com/'

app = Flask(__name__)

@app.route('/')
def home():
    
    text_dict = get_actual_lines(get_image_ocr(image_path='../Invoice scaled/invoice_2_scaled.png'))
    invoice_dict = get_region(text_dict=text_dict,keyword_list=['amount','total','amount (in usd)'])
    print(invoice_dict)

    data_list = get_data(text_dict=text_dict, region_dict=invoice_dict,is_numeric_data=True)
    print(data_list)

    invoice_data_dict = calc_total_and_tax(data_list)

    qty_dict = get_region(text_dict=text_dict,keyword_list=['qty', 'quantity'])

    qty_list = get_data(text_dict=text_dict, region_dict=qty_dict)
    
    qty_list = [i for i in qty_list if i!=None]

    print(qty_list)

    description_dict = get_region(text_dict=text_dict,keyword_list=['description','item & decription','item description'],reverse_keyword_method=True)

    item_description = get_data(text_dict=text_dict, region_dict=description_dict,is_numeric_data=False)
    print(item_description)
    
    vendor_name = " ".join(list([check(i+ ' is random') for i in list(text_dict[0].values())][0]['NNP']))
    
    print(vendor_name)

	# return render_template('home.html')


# @app.route('/predict',methods=['POST'])
# def predict():
#         return render_template('result.html',prediction = my_prediction, probability = probab*100.00)

if __name__ == '__main__':
	app.run(debug=True)