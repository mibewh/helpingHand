import os
from flask import Flask

app = Flask(__name__)
#app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug=True

@app.route('/')
def hello():
    return 'Hello World!'