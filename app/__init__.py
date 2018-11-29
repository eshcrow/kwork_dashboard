# -*- coding: utf-8 -*-

from flask import Flask
import click
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security


app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from models import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from routes import *

with app.app_context():
    db.create_all()


@app.cli.command()
def initdb():
    """Initialize the database."""
    db.drop_all()
    db.create_all()

    u1 = user_datastore.create_user(name='admin')
    u1.password_hash = generate_password_hash('admin')
    r1 = user_datastore.create_role(name='admin')
    u2 = user_datastore.create_user(name='moderator')
    u2.password_hash = generate_password_hash('moderator')
    r2 = user_datastore.create_role(name='moderator')

    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        print('Error: ', err)
    
    user_datastore.add_role_to_user(u1, r1)
    user_datastore.add_role_to_user(u2, r2)
    
    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        print('Error: ', err)
    print('Init DB: Success!')




@app.cli.command()
@click.argument('name')
@click.argument('passwd')
def adduser(name, passwd):
    """Add new user account"""
    u = user_datastore.create_user(name=name)
    u.password_hash = generate_password_hash(passwd)
    try:
        db.session.add(u)
        db.session.commit()
        print('User {} is created!'.format(name))
    except Exception as err:
        db.session.rollback()
        print('Error: ', err)