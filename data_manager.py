import psycopg2
import psycopg2.extras

from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def display_question(cursor):
    query = """
    SELECT question.id, submission_time, view_number, vote_number, title, message, image, username
    FROM question
    INNER JOIN users u on u.id = question.user_id
    ORDER BY submission_time DESC
    LIMIT 5
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def read_question(cursor):
    query = """
        SELECT question.id, submission_time, view_number, vote_number, title, message, image, username
        FROM question
        INNER JOIN users u on u.id = question.user_id
        ORDER BY id 
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_question(cursor, question_id):
    query = """
        SELECT answer.id, submission_time, vote_number, question_id, message, image, user_id, username
        FROM answer
        INNER JOIN users u on answer.user_id = u.id
        WHERE question_id = %(id)s
        ORDER BY submission_time 
    """
    cursor.execute(query, {"id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, question_id):
    query = """
        SELECT question.id, submission_time, view_number, vote_number, title, message, image, username
        FROM question
        INNER JOIN users u on u.id = question.user_id
        WHERE question.id = %(question_id)s
    """
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_id(cursor, answer_id):
    query = """
        SELECT a.id, submission_time, vote_number, question_id, message, image, user_id, username
        FROM answer a 
        INNER JOIN users u on a.user_id = u.id
        WHERE a.id = %(id)s
    """
    cursor.execute(query, {"id": answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_question_comments(cursor, id):
    query = """
        SELECT c.id, question_id, answer_id, message, submission_time, edited_count, user_id, username
        FROM comment c
        INNER JOIN users u on c.user_id = u.id
        WHERE question_id = %(id)s
        ORDER BY id DESC
        """

    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comments(cursor, id):
    query = """
        SELECT c.id, question_id, answer_id, message, submission_time, edited_count, user_id, username
        FROM comment c
        INNER JOIN users u on c.user_id = u.id
        WHERE answer_id = %(id)s
        ORDER BY id DESC
        """

    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def adding_new_question(cursor, question):
    query = """
            INSERT INTO question (title, message, image, user_id)
            VALUES(%(title)s, 
                    %(message)s,
                    %(image)s, 
                    %(user_id)s
                    );
            """
    cursor.execute(query, question)


@database_common.connection_handler
def adding_new_answer(cursor, answer):
    query = """
            INSERT INTO answer (message, question_id, image, user_id)
            VALUES ( %(message)s,
                    %(question_id)s,
                    %(image)s,
                    %(user_id)s
                    )   
            """
    cursor.execute(query, answer)


@database_common.connection_handler
def add_comment_to_question(cursor, comment):
    query = """
            INSERT INTO comment (message, question_id, user_id)
            VALUES      (%(message)s,
                        %(id)s,
                        %(user_id)s
                        )
        """
    cursor.execute(query, comment)


@database_common.connection_handler
def add_comment_to_answer(cursor, comment):
    query = """
        INSERT INTO comment (message, answer_id, user_id)
        VALUES (%(message)s,
                %(id)s,
                %(user_id)s
                )   
        """
    cursor.execute(query, comment)


@database_common.connection_handler
def edit_question(cursor, question):
    query = """
        UPDATE question 
        SET title= %(title)s, message = %(message)s
        WHERE id = %(id)s
        """
    cursor.execute(query, question)


@database_common.connection_handler
def edit_comment(cursor, comment):
    query = """
        UPDATE comment
        SET message = %(message)s, edited_count = edited_count + 1
        WHERE id = %(id)s
        """
    cursor.execute(query, comment)


@database_common.connection_handler
def get_comment_by_id(cursor, comment_id):
    query = """
        SELECT * FROM comment
        WHERE id = %(id)s
        """
    cursor.execute(query, {"id": comment_id })
    return cursor.fetchone()


@database_common.connection_handler
def edit_answer(cursor, answer_id):
    query = """
        UPDATE answer
        SET message = %(message)s
        WHERE id = %(id)s
        """
    cursor.execute(query, answer_id)


@database_common.connection_handler
def delete_comment(cursor, id):
    query = """
        DELETE FROM comment WHERE id = %(id)s
        """
    cursor.execute(query, {"id": id})


@database_common.connection_handler
def delete_answer(cursor, id):
    query = """
        DELETE FROM comment WHERE answer_id = %(id)s;
        DELETE FROM answer WHERE id = %(id)s;
        """
    cursor.execute(query, {"id": id})


@database_common.connection_handler
def delete_question(cursor, id):
    query = """
        DELETE FROM comment WHERE 
        answer_id IN (SELECT id FROM answer WHERE question_id = %(id)s)
        OR question_id = %(id)s;
        DELETE FROM answer WHERE question_id = %(id)s;
        DELETE FROM question WHERE id = %(id)s;
        """
    cursor.execute(query, {"id": id})


@database_common.connection_handler
def get_sorted_question(cursor, order_by, order_diretion):
    query = " SELECT * FROM question ORDER BY "
    cursor.execute(" ".join([query, order_by, order_diretion]))
    return cursor.fetchall()


@database_common.connection_handler
def search_for_questions(cursor, search):
    query = """
        SELECT * FROM question 
        WHERE message ILIKE %(search)s
        OR title ILIKE %(search)s
        """
    cursor.execute(query, {"search": f'%{search}%'})
    return cursor.fetchall()


@database_common.connection_handler
def add_info_to_database(cursor, info):
    query = """
        INSERT INTO users (username, password) 
        VALUES (%(username)s, %(password)s);
        """
    cursor.execute(query, info)


@database_common.connection_handler
def check_info(cursor, info):
    query = """
        SELECT * FROM users
        WHERE username = %(username)s
        """
    cursor.execute(query, info)
    return cursor.fetchone()


@database_common.connection_handler
def get_question_seq_value(cursor):
    query = """
        SELECT last_value 
        FROM question_id_seq
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_seq_value(cursor):
    query = """
        SELECT last_value 
        FROM answer_id_seq
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_users(cursor):
    query = """
        SELECT username, users.id, registration_date, 
            (SELECT count(q.id) as number_of_questions
            FROM question q
            WHERE q.user_id = users.id),
            
            (SELECT count(a.id) as number_of_answers
            FROM answer a 
            WHERE a.user_id = users.id), 
            
            (SELECT count(c.id) as number_of_comments
            FROM comment c 
            WHERE c.user_id = users.id)
        FROM users
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_user_details(cursor, user_id):
    query = """
        SELECT username, users.id, registration_date, 
            (SELECT count(q.id) as number_of_questions
            FROM question q
            WHERE q.user_id = users.id),
            
            (SELECT count(a.id) as number_of_answers
            FROM answer a 
            WHERE a.user_id = users.id), 
            
            (SELECT count(c.id) as number_of_comments
            FROM comment c 
            WHERE c.user_id = users.id)
        FROM users
        WHERE id = %(user_id)s
        """
    cursor.execute(query, {"user_id": user_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_question_per_user(cursor, id):
    query = """
        SELECT message, id FROM question
        WHERE user_id = %(id)s
        """
    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_per_user(cursor, id):
    query = """
            SELECT question_id, message, id FROM answer
            WHERE user_id = %(id)s
            """
    cursor.execute(query, {"id": id})
    return cursor.fetchall()


@database_common.connection_handler
def get_comment_per_user(cursor, id):
    query = """
            SELECT message, id, 
                CASE 
                    WHEN question_id is null THEN (SELECT question_id FROM answer WHERE answer.id=answer_id)
                    ELSE question_id
                END as link_question_id
            FROM comment
            WHERE user_id = %(id)s
            """
    cursor.execute(query, {"id": id})
    return cursor.fetchall()
