#!/usr/bin/env python

import sqlite3
import csv

def import_csv(cursor, fname, table):
    for row in csv.reader(open(fname)):
        cols = len(row)
        rowstr = ', '.join('?'*cols)
        cursor.execute('INSERT INTO %s VALUES (%s)' % (table, rowstr), row)

db = sqlite3.connect('db.sqlite3')
c = db.cursor()
import_csv(c, 'users.csv', 'LegacySite_user')
import_csv(c, 'products.csv', 'LegacySite_product')
db.commit()
db.close()
