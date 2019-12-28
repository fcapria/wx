#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import time
from datetime import datetime

db = TinyDB('db.json')



rightNow = datetime.now()

t = int(rightNow.strftime("%H%M"))
d = int(rightNow.strftime("%Y%m%d"))
temp = 3

db.insert({'date': d, 'time': t, 'temp': temp})

print(rightNow)
print(d)
print(t)

# Test data 
# Data format YYYYMMDDhhmm, temps in °F

# TinyDB stores each entry as a document

#print(db)