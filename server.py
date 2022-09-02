from flask import Flask, render_template, redirect, request, url_for, session

import cryptography
import data_manager
import connection
import time

import util

global user_questions
global user_answers

app = Flask(__name__)
app.secret_key = "32huifb1-9/?!-"


@app.route("/")
def main_page():
    if "username" not in session:
        return redirect(url_for('login_form'))
    return render_template("index.html", user_questions=data_manager.display_question())


@app.route("/list", methods=["GET", "POST"])
def qa_list():
    if "username" not in session:
        return redirect(url_for('login_form'))
    if 'order_by' in request.args:
        return render_template("index.html", user_questions=data_manager.get_sorted_question(
            request.args.get("order_by"), request.args.get("order_direction")))

    return render_template("index.html", user_questions=data_manager.read_question())


@app.route('/register', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        data_manager.add_info_to_database({
            "username": request.form.get("username"),
            "password": cryptography.hash_password(request.form.get("password"))
        })
        return redirect(url_for('main_page'))
    return render_template("register.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile_form():
    if request.method == 'POST':
        session.pop(
            "username"
        )
        return redirect(url_for('main_page'))
    return render_template('profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        info = {
            "username": request.form.get("username"),
            "password": request.form.get("password")
        }
        user = data_manager.check_info(info)
        if user:
            if cryptography.verify_password(info["password"], user['password']):
                session.update({
                    "username": user['username'],
                    "user_id": user['id']
                })
                return redirect(url_for('main_page'))
            return render_template('login.html', message='Incorrect Password')
        return render_template('login.html', message='Incorrect Username.')
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('username')
    session.pop('user_id')
    return redirect(url_for('main_page'))


@app.route("/search")
def search():
    questions = data_manager.search_for_questions(request.args.get("q"))
    return render_template("index.html", user_questions=questions)


@app.route("/question/<question_id>")
def question(question_id):
    questions = data_manager.get_question_by_id(question_id)
    question_comments = data_manager.get_question_comments(question_id)
    answers = data_manager.get_answers_by_question(question_id)
    for i in range(len(answers)):
        answers[i].update({"comments": data_manager.get_answer_comments(answers[i]["id"])})
        print(answers[i])
    # print(answers)
    return render_template("question.html",
                           user_questions=questions,
                           answers=answers,
                           question_comments=question_comments,
                           )


@app.route("/question/<question_id>/add-answer", methods=["GET", "POST"])
def add_new_answer(question_id):
    if request.method == "POST":
        data_manager.adding_new_answer(
            {"message": request.form.get("answer_title"),
             "question_id": question_id,
             "image": util.upload_picture(request.files.get("file"), "answer"),
             "user_id": session['user_id']
             }
        )
        return redirect(url_for("question", question_id=question_id))

    return render_template("new_answer.html", question_id=question_id)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        data_manager.adding_new_question(
            {
                "title": request.form.get("question_title"),
                "message": request.form.get("question"),
                "image": util.upload_picture(request.files.get("file"), "question"),
                "user_id": session['user_id']
            }
        )
        return redirect("/")

    return render_template("add_question.html")


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_new_comment(question_id):
    if request.method == "POST":
        data_manager.add_comment_to_question({
            "id": question_id,
            "message": request.form.get("question_comm"),
            "user_id": session['user_id']
        }
        )
        return redirect(url_for("question", question_id=question_id))
    return render_template("add_comm_to_question.html", question_id=question_id)


@app.route("/question/<question_id>/answer/<answer_id>/new-comment", methods=["GET", "POST"])
def add_new_answer_comment(answer_id, question_id):
    if request.method == "POST":
        data_manager.add_comment_to_answer({
            "id": answer_id,
            "message": request.form.get("question_comm"),
            "user_id": session['user_id']
        }
        )
        return redirect(url_for("question", question_id=question_id))
    return render_template("add_comm_to_question.html", question_id=question_id)


@app.route("/edit-question/<question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        data_manager.edit_question(
            {
                "id": question_id,
                "title": request.form.get("question_title"),
                "message": request.form.get("question_message"),
            }
        )
        return redirect("/")
    question = data_manager.get_question_by_id(question_id)
    return render_template(
        "edit_quesion.html", question_id=question_id, question=question
    )


@app.route("/edit-comment/<answer_id>")
def edit_comment(answer_id):
    if request.method == 'POST':
        data_manager.edit_comment(
            {
                "id": answer_id,
                "message": request.form.get("answer_comm"),
                "edited_count": request.form.get("edit_count")
            }
        )
        return redirect('/question/<question-id>')
    answer = data_manager.get_answer_by_id(answer_id)
    return render_template(
        "add_comm_to_answer.html", answer_id=answer_id, answer=answer
    )


@app.route('/question/<question_id>/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_question_comments(comment_id, question_id):
    if request.method == 'POST':
        data_manager.edit_comment(
            {"id": comment_id,
             "message": request.form.get("comment_message")}
        )
        return redirect(url_for('question', question_id=question_id))
    comment = data_manager.get_comment_by_id(comment_id)
    return render_template('edit_comments.html', comment=comment)


@app.route('/question/<question_id>/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id, question_id):
    if request.method == 'POST':
        data_manager.edit_answer({
            "id": answer_id,
            "message": request.form.get("answer_message")
        })
        return redirect(url_for('question', question_id=question_id))
    answer = data_manager.get_answer_by_id(answer_id)
    print(answer)
    return render_template('edit_answer.html', answer=answer)


@app.route('/comments/<comment_id>/delete')
def delete_comment(comment_id):
    comment = data_manager.get_comment_by_id(comment_id)
    print(comment)
    if comment['answer_id'] is None:
        question_id = comment['question_id']
    else:
        answer = data_manager.get_answer_by_id(comment['answer_id'])
        question_id = answer['question_id']
    data_manager.delete_comment(comment_id)
    return redirect(url_for("question", question_id=question_id))


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for('qa_list'))


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    data_manager.delete_answer(answer_id)
    return redirect(url_for('question', question_id=answer['question_id']))


@app.route('/users', methods=['GET', 'POST'])
def see_users():
    users = data_manager.get_users()
    return render_template("users.html", users=users)


@app.route('/user/<user_id>')
def get_user_details(user_id):
    user = data_manager.get_user_details(user_id)
    user.update({
        "questions": data_manager.get_question_per_user(user_id),
        "answers": data_manager.get_answer_per_user(user_id),
        "comments": data_manager.get_comment_per_user(user_id)
    })
    return render_template('user_details.html', user=user)


if __name__ == "__main__":
    app.run(
        debug=True
            )



















