from flask import Flask
from flask import redirect, render_template, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import secrets


app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
