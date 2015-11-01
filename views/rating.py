from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

rating = Blueprint('rating', __name__, template_folder=app.template_folder+'/rating')

