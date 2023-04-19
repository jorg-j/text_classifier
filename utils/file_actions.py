import json
import csv
import logging

logging.basicConfig(
    encoding='utf-8',
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(name)s: Line: %(lineno)s - %(funcName)s(): %(message)s",
)

def save_freqs_to_file(word_freqs, label_freqs, file_path):
    """
    Write word_freqs and label_freqs to a file as JSON.
    """
    freqs = {"word_freqs": word_freqs, "label_freqs": label_freqs}
    with open(file_path, 'w') as outfile:
        json.dump(freqs, outfile, sort_keys=True, indent=4)

def load_freqs_from_file(file_path):
    """
    Load word_freqs and label_freqs from a JSON file.
    """
    with open(file_path, 'r') as infile:
        freqs = json.load(infile)
    return freqs["word_freqs"], freqs["label_freqs"]


def csv_to_dict(filename):
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        result = {}
        for row in reader:
            result[row[0]] = row[1]
    return result

def import_training_data(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        texts = []
        labels = []
        for row in reader:
            texts.append(row[0])
            labels.append(row[1])
    return texts, labels