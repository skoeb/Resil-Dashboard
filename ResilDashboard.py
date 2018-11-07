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

cwd = os.getcwd()
siblings = os.listdir(cwd)

for i in siblings:
    if 'dsire' in str(i):
        dsirefolder = i

dsiremonth = int(dsirefolder.split('-')[-1])
currentmonth = datetime.now().month
currentyear = datetime.now().year

if currentmonth != dsiremonth:
    dirname = f'dsire-{currentyear}-{currentmonth}'
    os.makedirs(dirname)
    dsirezipurl = f'https://ncsolarcen-prod.s3.amazonaws.com/fullexports/dsire-{currentyear}-{currentmonth}.zip'
    r = requests.get(dsirezipurl)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(dirname)
    shutil.rmtree(dsirefolder)
    dsirefolder = dirname