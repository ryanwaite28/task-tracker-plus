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


def sign_up(request):
    data = json.loads(request.data)

    if "displayname" not in data:
        return jsonify(error = True, message = "Display Name field is required")

    if "email" not in data:
        return jsonify(error = True, message = "Email Address field is required")

    if "password" not in data:
        return jsonify(error = True, message = "Password field is required")

    if "confirmpassword" not in data:
        return jsonify(error = True, message = "Confirm Password field is required")

    displayname = cgi.escape( data['displayname'] )
    email = cgi.escape( data['email'] )
    password = cgi.escape( data['password'] ).encode('utf8')
    confirmpassword = cgi.escape( data['confirmpassword'] ).encode('utf8')

    if not displayname:
        return jsonify(error = True, message = "Display Name must be letters only; dashes, apostrophes and periods are allowed")

    if not email or chamber.isValidEmail(email) != True:
        return jsonify(error = True, message = "Email Address must be in proper format")

    if not password or len(password) < 6:
        return jsonify(error = True, message = "Password must be at least 6 characters")

    if not confirmpassword:
        return jsonify(error = True, message = "Confirm Password must be at least 6 characters")

    if password != confirmpassword:
        return jsonify(error = True, message = "Passwords must match")

    check_account = db_session.query(Users).filter_by(email = email).first()
    if check_account:
        return jsonify(error = True, message = "Email already in use")

    hash = bcrypt.hashpw(password, bcrypt.gensalt()).encode('utf8')
    new_user = Users(displayname = displayname, email = email, password = hash)
    db_session.add(new_user)
    db_session.commit()

    user_session["session_id"] = chamber.uniqueValue()
    user_session["you_id"] = new_user.id

    try:
        html = render_template("email/SignedUp.html", user = {"displayname": new_user.displayname})
        mail_sent = chamber.send_email(new_user.email, "Welcome!", "text/html", html)
        print("mail_sent", mail_sent)
    except Exception as e:
        print('error - ', e)
        pass

    return jsonify(message = "Signed Up!")


def create_task(request):
    data = json.loads(request.data)

    if "taskname" not in data:
        return jsonify(error = True, message = "Task Name field is required")

    taskname = cgi.escape(data['taskname'])

    if not taskname:
        return jsonify(error = True, message = "Task Name field cannot be blank")

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

    parent_task_id = data['parent_task_id'] if 'parent_task_id' in data else None

    new_task = Tasks(text = taskname, due_date = taskduedate, owner_id = user_session["you_id"]) \
        if taskduedate else Tasks(text = taskname, owner_id = user_session["you_id"])
    new_task.parent_task_id = parent_task_id
    db_session.add(new_task)
    db_session.commit()

    return jsonify(message = "New Task Created!", new_task = new_task.serialize)



def submit_password_reset_request(request):
    data = json.loads(request.data)

    if "email" not in data:
        return jsonify(error = True, message = "Email field is required")

    email = cgi.escape(data['email'])

    if not email:
        return jsonify(error = True, message = "Email field cannot be blank")

    check_account = db_session.query(Users).filter_by(email = email).first()
    if not check_account:
        return jsonify(error = True, message = "No account found by that email")

    check_reset_request = db_session.query(ResetPasswordRequests).filter_by(user_email = email).first()
    if check_reset_request:
        return jsonify(error = True, message = "Password reset already requested for this email")

    new_password_request = ResetPasswordRequests(user_email = email)
    db_session.add(new_password_request)
    db_session.commit()

    body = render_template("email/PasswordReset.html",
        data = {
            "user": check_account.serialize,
            "reset_request": new_password_request.serialize,
            "link": request.host + "/reset_password"
        }
    )
    mail_sent = chamber.send_email(check_account.email, "Password Reset Requested", "text/html", body)
    print("mail_sent", mail_sent)

    return jsonify(message = "New password reset requested!")
