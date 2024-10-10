from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import application

# User Model
class User(UserMixin, application.db.Model):
    id = application.db.Column(application.db.Integer, primary_key=True)
    username = application.db.Column(application.db.String(150), nullable = False, unique = True)
    password = application.db.Column(application.db.String(150), nullable = False)