#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 11:48:11 2018

@author: skoebric
"""
import os
import shutil
from datetime import datetime
import requests
import zipfile
import io
from github import Github

cwd = os.getcwd()
siblings = os.listdir(cwd)

for i in siblings:
    if 'dsire' in str(i):
        dirname = i

dsiremonth = int(dirname.split('-')[-1])
currentmonth = datetime.now().month
currentyear = datetime.now().year

if currentmonth != dsiremonth:
    newdirname = f'dsire-{currentyear}-{currentmonth}'
    accesstoken = '3702016da8b12f99d1ec127623863a2f72fbad55'
    os.makedirs(newdirname)
    dsirezipurl = f'https://ncsolarcen-prod.s3.amazonaws.com/fullexports/dsire-{currentyear}-{currentmonth}.zip'
    r = requests.get(dsirezipurl)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(newdirname)
    csvfiles = []
    for root,dirs,files in os.walk(newdirname):
        for file in files:
           if file.endswith(".csv"):
               df_ = pd.read_csv(os.path.join(newdirname, file))
               csvfiles.append(df_)

#    
#    
#    shutil.rmtree(dirname)
#    g = Github(accesstoken)
#    repo = g.get_repo("skoeb/Resil-Dashboard")
#    olddircontents = repo.get_contents(dirname)
#    repo.delete_file(olddircontents.path, "remove outdated DSIRE folder")
#    repo.create_file("test.txt", "test", "test", branch="test")    
#    
