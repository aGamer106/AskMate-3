from os.path import dirname, join, realpath

import data_manager

UPLOADS_PATH = join(dirname(realpath(__file__)), "static", "images")
# UPLOADS_PATH = "\\static\\images\\"


def upload_picture(file, owner_table):
    if file:
        filename = f"{owner_table}_id_{str(data_manager.get_question_seq_value().get('last_value') + 1) if owner_table == 'question' else str(data_manager.get_answer_seq_value().get('last_value') + 1)}.jpg"
        # path_to_file = UPLOADS_PATH + filename
        path_to_file = join(UPLOADS_PATH, filename)
        file.save(path_to_file)
        return "images/" + filename

    return ""


