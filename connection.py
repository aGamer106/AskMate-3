import csv
import os
import csv
import time
from datetime import datetime

import data_manager

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "question.csv")
DATA_HEADER = [
    "id",
    "submission_time",
    "view_number",
    "vote_number",
    "title",
    "message",
    "image",
]
ANSWERS_FILE_PATH = os.path.join(os.path.dirname(__file__), "answer.csv")


def get_all_questions():
    data_manager.read_question()


def add_new_questions(data):
    with open(DATA_FILE_PATH, "a") as csvfile:
        writer = csv.DictWriter(DATA_FILE_PATH, fieldnames=DATA_HEADER)
        print(data)
        writer.writerow(data)


def get_question(question_id):
    with open(DATA_FILE_PATH, "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == question_id:
                return row
    return " "


def add_new_answers(data):
    with open(ANSWERS_FILE_PATH, "a") as csvfile:
        writer = csv.DictWriter(ANSWERS_FILE_PATH, fieldnames=DATA_HEADER)
        writer.writerow(data)


def get_current_time():
    return datetime.utcfromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M:%S")
