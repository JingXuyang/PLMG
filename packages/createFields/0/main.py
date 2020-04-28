# -*- coding: utf-8 -*-

import os
import csv
import copy

import dbif


def createFields(db, project):
    print
    print 'Getting fields...'
    root = os.path.dirname(__file__)
    csvPath = os.path.join(root, 'fields.csv')
    data = []
    if os.path.isfile(csvPath):
        with open(csvPath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                d = copy.deepcopy(row)
                data.append(d)
    
    print
    print 'Creating fields...'
    for d in data:
        d['project'] = project
        print d
        
        if db.doesFieldExist(d['entity'], d['project'],
                             d['name']):
            print '  exists'
        else:
            print '  create'
            db.createField(**d)


if __name__ == '__main__':
    import sys
    project = sys.argv[1]
    
    db = dbif.CGT()
    createFields(db, project)


