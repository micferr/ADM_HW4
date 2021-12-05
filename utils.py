import csv
import pandas as pd


def load_clustering():
    with open("clusters.csv", 'r') as fin:
        reader = csv.reader(fin, delimiter=',')
        clustering = []
        for i, entry in enumerate(reader):
            if i == 0:
                continue
            clustering.append(entry[1])
    return clustering
