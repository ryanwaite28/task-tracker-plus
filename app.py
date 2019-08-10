# --- Modules/Functions --- #

import sqlite3, json, datetime, random, string, bcrypt

from functools import wraps
from datetime import timedelta
from threading import Timer

from flask import Flask, make_response, g, request, send_from_directory
from flask import render_template, url_for, redirect, flash, jsonify
from flask import session as user_session
from werkzeug.utils import secure_filename

from models import app_state

import handler_get as GET
import handler_post as POST
import handler_put as PUT
import handler_delete as DELETE




# --- Setup --- #

app = Flask(__name__)
app.secret_key = 'DF6Y#6G1$56F)$JD8*4G!?/Eoifht4gk90nit96dfs3TYD5$)F&*DFj/Y4DR'

def login_required(f):
    ''' Checks If User Is Logged In '''
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'session_id' in user_session:
            return f(*args, **kwargs)
        else:
            # flash('Please Log In To Use This Site.')
            return redirect('/signin')

    return decorated_function


def ajax_login_required(f):
    ''' Checks If User Is Logged In '''
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'session_id' in user_session:
            return f(*args, **kwargs)
        else:
            return jsonify(error = True, message = 'Not signed in')

    return decorated_function





# --- GET Routes --- #

@app.route('/', methods=['GET'])
def welcome():
    # db_session.rollback()
    # user_session.clear()
    return GET.welcome(request)


@app.route('/signup', methods=['GET'])
def signup():
    return GET.signup(request)


@app.route('/signin', methods=['GET'])
def signin():
    return GET.signin(request)


@app.route('/signout', methods=['GET'])
def signout():
    return GET.signout(request)


@login_required
@app.route('/home', methods=['GET'])
def home():
    return GET.home(request)



@app.route('/reset_password', methods=['GET'])
def reset_password():
    return GET.reset_password(request)


@app.route('/check_session', methods=['GET'])
def check_session():
    return GET.check_session(request)


@ajax_login_required
@app.route('/get_user_tasks', methods=['GET'])
def get_user_tasks():
    return GET.get_user_tasks(request)


@ajax_login_required
@app.route('/get_user_tasks/<int:task_id>', methods=['GET'])
def get_user_tasks_desc_id(task_id):
    return GET.get_user_tasks(request, task_id)


@ajax_login_required
@app.route('/tasks/<int:task_id>/get_children', methods=['GET'])
def get_task_children(task_id):
    return GET.get_task_children(request, task_id)


@ajax_login_required
@app.route('/tasks/<int:parent_task_id>/get_children/<int:child_task_id>', methods=['GET'])
def get_task_children_desc_id(parent_task_id, child_task_id):
    return GET.get_task_children_desc_id(request, parent_task_id, child_task_id)


@ajax_login_required
@app.route('/get_user_tasknotes', methods=['GET'])
def get_user_tasknotes():
    return GET.get_user_tasknotes(request)


@ajax_login_required
@app.route('/get_user_tasknotes/<int:tasknote_id>', methods=['GET'])
def get_user_tasknotes_desc_id(tasknote_id):
    return GET.get_user_tasknotes(request, tasknote_id)




# --- POST Routes --- #

@app.route('/sign_up', methods=['POST'])
def sign_up():
    return POST.sign_up(request)


@app.route('/submit_password_reset_request', methods=['POST'])
def submit_password_reset_request():
    return POST.submit_password_reset_request(request)


@ajax_login_required
@app.route('/create_task', methods=['POST'])
def create_task():
    return POST.create_task(request)


@ajax_login_required
@app.route('/create_subtask', methods=['POST'])
def create_subtask():
    return POST.create_subtask(request)


@ajax_login_required
@app.route('/create_tasknote', methods=['POST'])
def create_tasknote():
    return POST.create_tasknote(request)


@ajax_login_required
@app.route('/create_subtasknote', methods=['POST'])
def create_subtasknote():
    return POST.create_subtasknote(request)




# --- PUT Routes --- #

@app.route('/sign_in', methods=['PUT'])
def sign_in():
    return PUT.sign_in(request)


@app.route('/submit_password_reset_code', methods=['PUT'])
def submit_password_reset_code():
    return PUT.submit_password_reset_code(request)


@ajax_login_required
@app.route('/update_account', methods=['PUT'])
def update_account():
    return PUT.update_account(request)


@ajax_login_required
@app.route('/update_password', methods=['PUT'])
def update_password():
    return PUT.update_password(request)


@ajax_login_required
@app.route('/update_icon', methods=['PUT'])
def update_icon():
    return PUT.update_icon(request)


@ajax_login_required
@app.route('/update_task', methods=['PUT'])
def update_task():
    return PUT.update_task(request)


@ajax_login_required
@app.route('/update_subtask', methods=['PUT'])
def update_subtask():
    return PUT.update_subtask(request)


@ajax_login_required
@app.route('/update_tasknote', methods=['PUT'])
def update_tasknote():
    return PUT.update_tasknote(request)


@ajax_login_required
@app.route('/update_subtasknote', methods=['PUT'])
def update_subtasknote():
    return PUT.update_subtasknote(request)


@ajax_login_required
@app.route('/toggle_task_done', methods=['PUT'])
def toggle_task_done():
    return PUT.toggle_task_done(request)


@ajax_login_required
@app.route('/toggle_subtask_done', methods=['PUT'])
def toggle_subtask_done():
    return PUT.toggle_subtask_done(request)




# --- DELETE Routes --- #

@ajax_login_required
@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    return DELETE.delete_account(request)


@ajax_login_required
@app.route('/delete_task', methods=['DELETE'])
def delete_task():
    return DELETE.delete_task(request)


@ajax_login_required
@app.route('/delete_subtask', methods=['DELETE'])
def delete_subtask():
    return DELETE.delete_subtask(request)


@ajax_login_required
@app.route('/delete_tasknote', methods=['DELETE'])
def delete_tasknote():
    return DELETE.delete_tasknote(request)


@ajax_login_required
@app.route('/delete_subtasknote', methods=['DELETE'])
def delete_subtasknote():
    return DELETE.delete_subtasknote(request)





# --- Listen --- #


if __name__ == "__main__":
    app.debug = True
    app.run( host = '0.0.0.0' , port = 8000 )
