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


def delete_task(request):
    data = json.loads(request.data) if request.data else None

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

    db_session.delete(task)
    db_session.commit()

    return jsonify(success = True, message = "Task deleted!")
