#!/usr/bin/env python
# coding: utf-8

import os
import requests
import time
import pandas as pd


# data = {"username": "pranavpawar3@gmail.com", "password": "Googleyash46"}
data = {"username": "pipodab832@kartk5.com", "password": "dataBrewers1"}
auth_token = requests.post('https://api.elis.rossum.ai/v1/auth/login',data=data).json()['key']

que_url = requests.get('https://api.elis.rossum.ai/v1/queues?page_size=1',
            headers={'Authorization': f'Token {auth_token}'}).json()['results'][0]['url']

que_id = que_url.split('/')[-1]

import requests

filepath = "./Round 2/Round 2 invoices (15).pdf"

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

print("The file is reachable at the following URL:{}, and this id {}".format(annotation_url,doc_id))


## lets give it some time to process
time.sleep(5)

import time
okay=True
while okay:
    if requests.get('{}'.format(annotation_url),
            headers={'Authorization': f'Token {auth_token}'}).json()['status'] == 'to_review':
        print('okay done!! Lets see...')
        okay=False
    else:
        print('not ready yet! might take a minute to process...')
        time.sleep(40)
        

import requests

response = requests.get('{}/export?status=to_review&format=csv&id={}'.format(que_url,doc_id),
            headers={'Authorization': f'Token {auth_token}'})


import csv

f = open("./csv_outputs/{}_outputs.csv".format(filepath.split('/')[-1].strip('.pdf')), "wb")
# writer = csv.writer(f)
# writer.writerows(str(response.content).split('\\n'))
f.write(response.content)
f.close()

response.content#.json()



df = pd.read_csv('./csv_outputs/Round 2 invoices (11)_outputs.csv')

primary_df = df.loc[:,:'Notes'].drop_duplicates().T

item_df = df.loc[:,'Description':]


# ### Push the data to MongoDB

# In[545]:


import pandas as pd
import pymongo
import json
import sys, getopt, pprint


# In[556]:


myclient = pymongo.MongoClient('mongodb://192.168.1.106:27017/')
db = myclient['ABInBev']
col = db["invoices"]


# In[582]:


df = pd.read_csv('./csv_outputs/Round 2 invoices (11)_outputs.csv')
# headers_string = "Invoice Number,PO Number,Invoice Date,Due Date,Account Number,Bank Code,IBAN,BIC/SWIFT,Payment Reference,Specific Symbol,Subtotal,Total Tax,Total Amount,Due Amount,Currency,Vendor Name,Vendor Address,Vendor VAT Number,Customer Name,Customer VAT Number,Notes,Description,Quantity,Amount Base,Tax Rate,Total Amount"
# df.columns =  [str(i) for i in headers_string.split(',')]

df = df.rename(columns={'Total Amount.1':'Amount Item'})


# In[583]:


df.to_json('yourjson.json')


# In[584]:


jdf = open('yourjson.json').read()                        # loading the json file 
data = json.loads(jdf)


# In[585]:


data


# In[586]:


# csvfile = open('./csv_outputs/Round 2 invoices (13)_outputs.csv', 'r')
# reader = csv.DictReader( csvfile )


# In[587]:


# headers_string = "Invoice Number,PO Number,Invoice Date,Due Date,Account Number,Bank Code,IBAN,BIC/SWIFT,Payment Reference,Specific Symbol,Subtotal,Total Tax,Total Amount,Due Amount,Currency,Vendor Name,Vendor Address,Vendor VAT Number,Customer Name,Customer VAT Number,Notes,Description,Quantity,Amount Base,Tax Rate,Total Amount"
# header = [str(i) for i in headers_string.split(',')]


# for each in reader:
#     row={}
#     for field in header:
#         row[field]=each[field]

#     col.insert_one(row)


# In[588]:


col.insert_one(data)


# In[589]:


myclient['ABInBev'].collection_names()


# In[590]:


def insert_data(filepath):
    df = pd.read_csv(filepath)
    df = df.rename(columns={'Total Amount.1':'Amount Item'})
    df.to_json('yourjson.json')
    jdf = open('yourjson.json').read() # loading the json file 
    data = json.loads(jdf)
    col.insert_one(data)


# In[592]:


# insert_data('./csv_outputs/Round 2 invoice (1).jpg_outputs.csv')


# ### Load the MongoDB data!

# In[593]:


cursor = col.find()
mongo_docs = list(cursor)


# In[598]:


pd.DataFrame.from_dict(mongo_docs[2])


# In[607]:


all_data = pd.DataFrame()
for doc in mongo_docs:
    all_data = all_data.append(pd.DataFrame.from_dict(doc))


# In[608]:


all_data


# In[609]:


all_data.to_csv('all_data.csv',index=False, header=True)


# In[ ]:




