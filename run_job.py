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

logging.getLogger().setLevel(logging.INFO)

import argparse
from IPython import get_ipython
# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--task", "-t",default='file', help="Type of task, file or batch!")
parser.add_argument("--source_path", "-p", help="Source File or Dir Path")
parser.add_argument("--csv_path", "-c", default='../csv_outputs/', help="path to save the CSV files")

# Read arguments from the command line
args = parser.parse_args()
csv_path_dir = args.csv_path

# data = {"username": "pranavpawar3@gmail.com", "password": "Googleyash46"}
data = {"username": "pipodab832@kartk5.com", "password": "dataBrewers1"}
auth_token = requests.post('https://api.elis.rossum.ai/v1/auth/login',data=data).json()['key']

que_url = requests.get('https://api.elis.rossum.ai/v1/queues?page_size=1',
            headers={'Authorization': f'Token {auth_token}'}).json()['results'][0]['url']

que_id = que_url.split('/')[-1]

logging.info('credentials loaded!')


def get_data(filepath, data,csv_path_dir):
        queue_id = que_id #47431
        username = data['username']
        password = data['password']
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

        if not os.path.exists(csv_path_dir):
            os.mkdir(csv_path_dir)

        path = "{}/{}_outputs.csv".format(csv_path_dir, filepath.split('/')[-1].strip('.pdf'))

        # if not os.path.exists('../csv_outputs/'):
        #     os.mkdir('../csv_outputs')

        # path = "../csv_outputs/{}_outputs.csv".format(filepath.split('/')[-1].strip('.pdf'))

        f = open(path, "wb")
        # writer = csv.writer(f)
        # writer.writerows(str(response.content).split('\\n'))
        f.write(response.content)
        f.close()
        logging.info('extracted data saved in csv format at {}'.format(path))

if __name__=='__main__':
    if args.task == 'file':
        filepath = args.source_path
        try:
            get_data(filepath,data,csv_path_dir)
        except:
            logging.warning('File path or format is invalid, cannot save, please try again!!')
        
    if args.task == 'batch':
        files = os.listdir(args.source_path)
        logging.info('extracting data from {} files'.format(len(files)))
        for filename in tqdm.tqdm(files):
            try:
                filepath = os.path.join(args.source_path,filename)
                get_data(filepath,data,csv_path_dir)
            except:
                logging.warning('File path or format is invalid,cannot save, please try again!!')
        
        logging.info('Job finished check status...')
                    
    
