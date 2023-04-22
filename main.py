import csv
import json
import re
import string
from collections import defaultdict
from loguru import logger

logger.add("logs.log", retention="1 week")


from utils.file_actions import (
    csv_to_dict,
    import_training_data,
    load_freqs_from_file,
    save_freqs_to_file,
)

from utils.text_normalisation import contractions, stem_sentence



def train(texts, labels):
    """
    Train a Naive Bayes classifier on a list of texts and labels.
    """

    logger.info("Training text and labels")
    word_freqs = defaultdict(lambda: defaultdict(int))
    label_freqs = defaultdict(int)

    for text, label in zip(texts, labels):
        for word in preprocess(text):
            word_freqs[word][label] += 1
        label_freqs[label] += 1

    return word_freqs, label_freqs


def preprocess(text):
    """
    Preprocess a text by converting it to lowercase, removing punctuation, and removing conduction words.
    """
    text = text.lower()
    text = contractions(text)
    # text = stem_sentence(text)
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
    conduction_words = [
        "and",
        "or",
        "but",
        "if",
        "then",
        "else",
        "for",
        "of",
        "a",
        "an",
        "the",
    ]
    try:
        with open("banned.txt", "r")as f:
            banned = f.read().splitlines()
        conduction_words.extend(banned)
    except:
        pass

    words = text.split()
    filtered_words = [word for word in words if word not in conduction_words]
    return filtered_words


def predict(text, word_freqs, label_freqs, word_boosts):
    """
    Predict the label of a text using a Naive Bayes classifier with word boosts for specific labels.
    """
    logger.info("Predicting")
    words = preprocess(text)
    scores = {
        label: label_freqs[label] / sum(label_freqs.values()) for label in label_freqs
    }

    for word in words:
        if word in word_freqs:
            for label in label_freqs:
                a = word in word_boosts
                try:
                    if word not in word_boosts:
                        # Apply a boost to the score for this label
                        apply = (word_freqs[word][label] + 1)* 2 / (sum(word_freqs[word].values()) + len(word_freqs))
                        scores[label] *= apply
                    else:
                        apply = (word_freqs[word][label] + 1) / (sum(word_freqs[word].values()) + len(word_freqs))
                        scores[label] *= apply
                except:
                    pass
    logger.debug(max(scores, key=scores.get))
    return max(scores, key=scores.get)


def training_mode(phrase, result, items):
    print("\n\n\n")
    logger.info(f"Training Phrase: {phrase}")
    logger.info(f"Original Result: {result}")

    print("Select an item from the list:")
    for i, item in enumerate(items):
        print(f"{i+1}. {item}")

    # Get user input and validate it
    while True:
        choice = input("Enter the number of the item you want: ")
        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        choice = int(choice)
        if choice < 1 or choice > len(items):
            print(f"Invalid choice. Please enter a number between 1 and {len(items)}.")
            continue
        break

    # Print the selected item
    print(f"You selected: {items[choice-1]}")
    result = items[choice - 1]
    logger.info(f"User Selected: {result}")
    return result


def process_string(phrase, boosts):
    logger.info(f"Processing: {phrase}")
    train_mode = False

    texts, labels = import_training_data("training_data.csv")
    word_freqs, label_freqs = train(texts, labels)

    # Save the Frequencies to JSON
    save_freqs_to_file(word_freqs, label_freqs, "freqs.json")

    logger.info(f"Training Mode: {train_mode}")
    result = predict(phrase, word_freqs, label_freqs, boosts)
    logger.info(f"{phrase}: {result}")

    if train_mode:
        logger.info("Training Mode is Active")
        normalised_labels = list(set(labels))
        phrase = phrase.replace(",", "").replace("\n", "")
        result = training_mode(phrase, result, normalised_labels)

        with open("training_data.csv", "a+") as f:
            f.write(f"{phrase},{result}\n")


def main():
    logger.info("Loading Boosts")
    boosts = csv_to_dict("boost.csv")
    logger.debug(boosts)

    try:
        with open("data_in.csv", "r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("File: data_in.csv is not found")
        data = []

    for line in data:
        process_string(line, boosts)

if __name__ == "__main__":
    main()