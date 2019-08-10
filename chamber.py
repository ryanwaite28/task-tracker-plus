import os , sys , cgi , re, requests, datetime
import logging, sqlite3, json, random, string

import sendgrid, cloudinary
from sendgrid.helpers.mail import *
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'])
ALLOWED_PHOTOS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_VIDEOS = set(['mp4'])

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')

cloudinary_env_proper = CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET and CLOUDINARY_CLOUD_NAME

if cloudinary_env_proper:
  cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME, 
    api_key = CLOUDINARY_API_KEY, 
    api_secret = CLOUDINARY_API_SECRET
  )

sg = None
if SENDGRID_API_KEY:
  sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


def send_email(email, subject, mimetype, body):
    try:
        from_email = Email("app113835630@heroku.com")
        to_email = Email(email)
        subject = subject
        content = Content(mimetype, body)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body = mail.get())

        print("response", response)
        return {"error": None, "successful": True, "response": response}

    except Exception as err:
        print(err)
        return {"error": err, "successful": False}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def allowed_photo(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_PHOTOS

def allowed_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_VIDEOS

def uniqueValue():
    value = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(50))
    return value.lower()

def isValidEmail(email):
    if len(email) > 7:
        if re.match("[\w.-]+@[\w.-]+", email) != None:
            return True
        else:
            return False
    else:
        return False


def uploadFile(file, old_id = None):
    try:
        if not file:
            return False

        upload_result = upload(file)
        thumbnail_url1, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=200, height=200)

        data_dict = {
            "upload_result": upload_result,
            "thumbnail_url1": thumbnail_url1,
            "options": options
        }

        return data_dict

    except Exception(e):
        print("error - ", e)
        return False
