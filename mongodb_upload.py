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
import tqdm

import pymongo
import json
import getopt, pprint


logging.getLogger().setLevel(logging.INFO)

import argparse
from IPython import get_ipython
# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--path", "-p", help="Directory Path where all the csv files are stored")
parser.add_argument("--get_complete_data","-g",default='y', help="Get a collated file for all the invoice reports")
parser.add_argument("--upload","-u",default='y', help="upload data to the DB")


# Read arguments from the command line
args = parser.parse_args()

myclient = pymongo.MongoClient('mongodb://192.168.1.106:27017/')
db = myclient['ABInBev']
col = db["invoices"]

def upload(filepath,col):
    df = pd.read_csv(filepath)

    df = df.rename(columns={'Total Amount.1':'Item Amount'})

    df.to_json('yourjson.json')

    jdf = open('yourjson.json').read()
    data = json.loads(jdf)

    col.insert_one(data)


if __name__=="__main__":
    if args.upload=='y':
        files = os.listdir(args.path)
        logging.info('Uploading {} files to the database'.format(len(files)))
        for filename in files:
            try:
                filepath = os.path.join(args.path,filename)
                upload(filepath,col)

            except:
                logging.warning('CAUTION :file {} empty/ not present/ invalid'.format(filename))

    if args.get_complete_data == 'y':
        try:
            cursor = col.find()
            mongo_docs = list(cursor)
            logging.info("Collating results from {} docs".format(len(mongo_docs)))
            all_data = pd.DataFrame()
            for doc in mongo_docs:
                try:
                    all_data = all_data.append(pd.DataFrame.from_dict(doc))
                except:
                   logging.warning("df keys mistmatch, couldn't append, moving on next, check the file id {}".format(doc['_id'])) 

            all_data.to_csv('all_data.csv',index=False, header=True)
        
        except:
            logging.warning('Data not present or invalid DB connection')


