import os , sys , cgi , re, requests, datetime, bcrypt
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


def sign_in(request):
    data = json.loads(request.data)
    print('--- data ---', data)

    if "email" not in data:
        return jsonify(error = True, message = "Email Address field is required")

    if "password" not in data:
        return jsonify(error = True, message = "Password field is required")

    email = cgi.escape( data['email'] )
    password = cgi.escape( data['password'] ).encode('utf8')

    if not email or chamber.isValidEmail(email) != True:
        return jsonify(error = True, message = "Email Address must be in proper format")

    if not password:
        return jsonify(error = True, message = "Password must be at least 6 characters")

    you = db_session.query(Users).filter_by(email = email).first()
    if not you:
        return jsonify(error = True, message = "Invalid credentials")

    checkPassword = bcrypt.hashpw(password, you.password.encode('utf8'))
    if checkPassword != you.password:
        return jsonify(error = True, message = "Invalid credentials")

    you.last_loggedin = func.now()
    db_session.add(you)
    db_session.commit()

    user_session["session_id"] = chamber.uniqueValue()
    user_session["you_id"] = you.id

    return jsonify(message = "Signed In!")



def toggle_task_done(request):
    data = json.loads(request.data) if request.data else None
    print('data - ', data)

    if not data:
        return jsonify(error = True, message = "request data not provided")
    if 'id' not in data:
        return jsonify(error = True, message = "id not provided in request data")

    you_id = user_session['you_id']
    task_id = int(data['id'])

    task = db_session.query(Tasks).filter_by(id = task_id).first()
    if not task:
        return jsonify(error = True, message = "Could not find task by given id")
    if task.owner_id != you_id:
        return jsonify(error = True, message = "Current user does not own this task")

    task.done = not data['done']
    task.last_updated = func.now()
    db_session.add(task)
    db_session.commit()

    return jsonify(success = True, message = "Task Updated!", task = task.serialize)


def update_account(request):
    data = json.loads(request.data) if request.data else None

    if not data:
        return jsonify(error = True, message = "request data not provided")
    if 'displayname' not in data:
        return jsonify(error = True, message = "displayname not provided in request data")
    if 'email' not in data:
        return jsonify(error = True, message = "email not provided in request data")

    displayname = cgi.escape( data['displayname'] )
    email = cgi.escape( data['email'] )

    if not displayname:
        return jsonify(error = True, message = "displayname must have value")

    you = db_session.query(Users).filter_by(id = user_session['you_id']).one()

    you.displayname = displayname
    if you.email != email:
        check_email = db_session.query(Users).filter_by(email = email).first()
        if check_email:
            return jsonify(error = True, message = "Email is already in use")

    you.email = email
    db_session.add(you)
    db_session.commit()

    return jsonify(message = "Account Updated!", you = you.serialize)



def update_password(request):
    data = json.loads(request.data) if request.data else None

    if not data:
        return jsonify(error = True, message = "request data not provided")
    if 'oldpassword' not in data:
        return jsonify(error = True, message = "oldpassword not provided in request data")
    if 'password' not in data:
        return jsonify(error = True, message = "password not provided in request data")
    if 'confirmpassword' not in data:
        return jsonify(error = True, message = "confirmpassword not provided in request data")

    oldpassword = cgi.escape( data['oldpassword'] ).encode('utf8')
    password = cgi.escape( data['password'] ).encode('utf8')
    confirmpassword = cgi.escape( data['confirmpassword'] ).encode('utf8')

    if password != confirmpassword:
        return jsonify(error = True, message = "Passwords must match")

    you = db_session.query(Users).filter_by(id = user_session['you_id']).one()
    checkPassword = bcrypt.hashpw(oldpassword, you.password.encode('utf8'))
    if checkPassword != you.password:
        return jsonify(error = True, message = "Old password is incorrect")

    hash = bcrypt.hashpw(password, bcrypt.gensalt()).encode('utf8')
    you.password = hash
    db_session.add(you)
    db_session.commit()

    return jsonify(message = "Password Updated!")


def update_icon(request):
    file = request.files['icon_file']
    if not file:
        return jsonify(error = True, message = "File not found in request")

    try:
        res = chamber.uploadFile(file)
        icon_id = res["upload_result"]["public_id"]
        icon_url = res["upload_result"]["secure_url"]
        you = db_session.query(Users).filter_by(id = user_session['you_id']).one()
        you.icon = icon_url
        you.icon_id = icon_id
        db_session.add(you)
        db_session.commit()

        return jsonify(message = "Icon Updated!", you = you.serialize)
    except Exeption as e:
        print('error - ', e)
        return jsonify(error = True, message = "could not upload image at this time")


def update_task(request):
    data = json.loads(request.data)
    print('data - ', data)

    if "taskname" not in data:
        return jsonify(error = True, message = "Task Name field is required")
    if "task_id" not in data:
        return jsonify(error = True, message = "Task id field is required")

    taskname = cgi.escape(data['taskname'])
    task_id = data['task_id']

    if not taskname:
        return jsonify(error = True, message = "Task Name field cannot be blank")
    if not task_id:
        return jsonify(error = True, message = "Task id field cannot be blank")

    taskduedate = None
    if "taskduedate" in data:
        if data['taskduedate']:
            date_obj = datetime.strptime(data['taskduedate'], "%Y-%m-%d")
            current = datetime.now()
            print(date_obj, current)
            if date_obj < current:
                return jsonify(error = True, message = "Date cannot be today or in the past")
            else:
                taskduedate = date_obj


    task = db_session.query(Tasks).filter(Tasks.id == task_id).filter(Tasks.owner_id == user_session["you_id"]).first()
    if not task:
        return jsonify(error = True, message = "Task not found...")

    task.text = taskname
    task.due_date = taskduedate
    db_session.add(task)
    db_session.commit()

    return jsonify(message = "Task Updated!", task = task.serialize)


def submit_password_reset_code(request):
    data = json.loads(request.data)

    if "code" not in data:
        return jsonify(error = True, message = "Code field is required")

    code = cgi.escape(data['code'])

    if not code:
        return jsonify(error = True, message = "Code field cannot be blank")

    reset_request = db_session.query(ResetPasswordRequests).filter_by(unique_value = code).first()
    if not reset_request:
        return jsonify(error = True, message = "Invalid code")

    you = db_session.query(Users).filter_by(email = reset_request.user_email).first()
    new_password = chamber.uniqueValue()
    hash = bcrypt.hashpw(new_password, bcrypt.gensalt()).encode('utf8')

    print("reset - ", new_password, hash, you)

    you.password = hash

    db_session.add(you)
    db_session.delete(reset_request)
    db_session.commit()

    checkPassword = bcrypt.hashpw(new_password, you.password.encode('utf8'))
    if checkPassword != you.password:
        print("new password test failed...")
        return jsonify(error = True, message = "Server error: could not reset password...")
    else:
        print("new password test successful!")
        body = render_template("email/PasswordResetSuccess.html",
            data = {
                "user": you.serialize_small,
                "password": new_password,
                "link": request.host + "/signin"
            }
        )
        mail_sent = chamber.send_email(you.email, "Password Reset Successful!", "text/html", body)

        return jsonify(message = "New password reset successful! Check your email.")
