import pandas as pd
import numpy as np
import requests
import os
import sys
import requests
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from io import BytesIO


def get_image_ocr(image_path=None):
    # Add your Computer Vision subscription key and endpoint to your environment variables.
    if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
        subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
    else:
        print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
        sys.exit()

    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
        endpoint = os.environ['COMPUTER_VISION_ENDPOINT']

    ocr_url = endpoint + "vision/v3.0/ocr"

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'language': 'unk', 'detectOrientation': 'true'}

#     image_path = "./Invoice Format/invoices (9).jpg"
    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    # Set Content-Type to octet-stream
    headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
    # put the byte array into your post request
    response = requests.post(ocr_url, headers=headers, params=params, data = image_data)

    analysis = response.json()
    
    return analysis

def get_actual_lines(analysis):
    actual_lines = dict()
    for region_no, region in enumerate(analysis['regions']):
        actual_lines[region_no] = {}
        for line_no, lines in enumerate(region['lines']):
            text_colab = []
            for single_line in lines['words']:
                 text_colab.append(single_line['text'])
            actual_lines[region_no][line_no] = ' '.join(text_colab)
    
    return actual_lines

def convert_float(num):
    strip_this = "()-+!@#%^&*%$[]\|;:,<>/?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ## don't include full stop (dot) in this strip_this list
    for i in strip_this:
        num = num.replace(i, '')
    try:
        return float(num.strip(strip_this).strip())
    except:
        return None
        
def get_region(text_dict=None,keyword_list=[],reverse_keyword_method=False):
    
    region_dict = dict()
    trigger = None

    for region_no in range(len(text_dict)):
        for word in list(text_dict[region_no].values()):
            if not reverse_keyword_method:
                if word.lower() in keyword_list:
                    print(f'found {word} in region {region_no}')
                    trigger = word
                    region_dict[region_no] = trigger
            else:
                if True in [i in word.lower() for i in keyword_list]:
                    print(f'found {word} in region {region_no}')
                    trigger = word
                    region_dict[region_no] = trigger

    
    return region_dict


def get_data(text_dict=None,region_dict=None, is_numeric_data=True):
    strip_this = "()-+!@#%^&*%$[]\|;:,<>/?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    get_list = []
    for key in list(region_dict.keys()):

        try:
            get_list = [i.lower() for i in list(text_dict[key].values())]
            get_list = get_list[get_list.index(region_dict[key].lower())+1:]  
            if is_numeric_data:
                get_list = [convert_float(i) for i in get_list]

        except:
            print('not possible for region {}'.format(key))
            get_list=None
            continue
    return get_list

def calc_total_and_tax(invoice_data_list=None):
    actual_total = 0
    for i in invoice_data_list:
        try:
    #         if actual_total!=float((i.strip(strip_this)).strip()):
    #             actual_total+=float(i.strip(strip_this).strip())
            if actual_total!=i:
                actual_total+=i
            else:
                break
        except:
            print('no')

    # final_total = float((invoice_data_list[-1].strip(strip_this)).strip())
    try:
        final_total = invoice_data_list[-1]
        tax_and_extra = (final_total - actual_total)
        print('\n', actual_total,'\n' ,final_total,'\n', tax_and_extra)
    except:
        print('no data available')
        final_total = np.nan
        tax_and_extra = np.nan
    
    return {'actual_total':actual_total,'final_total':final_total, 'tax_and_extra':tax_and_extra}

def findtags(tag_prefix, tagged_text):
        """
        Find tokens matching the specified tag_prefix
        """
        import nltk

        cfd = nltk.ConditionalFreqDist((tag, word) for (word, tag) in tagged_text
                                      if tag.startswith(tag_prefix))
        return dict((tag, cfd[tag].keys()) for tag in cfd.conditions())

# Tokenize the raw text 
def check(text):
    import nltk

    lTokens = nltk.word_tokenize(text)

    # Tag the tokens with their type - ie are they nouns or not
    lTokens = nltk.pos_tag(lTokens)

    # find all the proper nouns and print them out
    lTagDict = findtags('NNP', lTokens)
#     for tag in sorted(lTagDict):
#         print(tag, lTagDict[tag])
    return lTagDict

