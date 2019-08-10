import os , sys , cgi , re, requests, datetime
import logging, sqlite3, json, random, string
from datetime import datetime

import chamber

from models import Base, db_session
from models import Users, Tasks, Notifications, ResetPasswordRequests

from flask import Flask, make_response, g, request, send_from_directory
from flask import render_template, url_for, redirect, flash, jsonify
from flask import session as user_session
from werkzeug.utils import secure_filename

from sqlalchemy import cast, exc, select
from sqlalchemy import desc, or_
from sqlalchemy.sql import func
from sqlalchemy.exc import InvalidRequestError, ArgumentError
from sqlalchemy.exc import StatementError, OperationalError, InternalError


def welcome(request):
    if 'session_id' in user_session:
        return redirect('/home')

    return render_template('welcome.html', signed_in = 'session_id' in user_session)


def signin(request):
    if 'session_id' in user_session:
        return redirect('/home')

    return render_template('signin.html', signed_in = 'session_id' in user_session)


def signup(request):
    if 'session_id' in user_session:
        return redirect('/home')

    return render_template('signup.html', signed_in = 'session_id' in user_session)


def signout(request):
    user_session.clear()
    return redirect('/')


def home(request):
    if 'session_id' not in user_session:
        return redirect('/')
    return render_template('home.html', signed_in = 'session_id' in user_session)


def reset_password(request):
    if 'session_id' in user_session:
        return redirect('/home')

    return render_template('reset-password.html', signed_in = 'session_id' in user_session)



def check_session(request):
    if 'session_id' not in user_session:
        return jsonify(online = False)

    you = db_session.query(Users).filter_by(id = user_session['you_id']).one()
    return jsonify(online = True, user = you.serialize)


def get_user_tasks(request, task_id = None):
    you_id = user_session['you_id']

    tasks = db_session.query(Tasks) \
        .filter(Tasks.owner_id == you_id) \
        .filter(Tasks.id < task_id) \
        .filter(Tasks.parent_task_id == None) \
        .order_by(desc(Tasks.id)).limit(5).all() if task_id \
    else db_session.query(Tasks) \
        .filter_by(owner_id = you_id) \
        .filter(Tasks.parent_task_id == None) \
        .order_by(desc(Tasks.id)).limit(5).all()

    return jsonify(tasks = [t.serialize for t in tasks])
