import os
import csv

DIR = os.path.dirname(os.path.realpath(__file__))


def get_csv_data(filename):
    lines = []
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        for row in reader:
            lines.append(row)
    return lines


def get_data(filename):
    return get_csv_data(os.path.join(DIR, "data", filename))

