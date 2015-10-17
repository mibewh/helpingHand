from flask import Flask, render_template


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug=True

@app.route('/')
def hello_world():

	return render_template('index.jade', testvar='hiya')

if __name__ == '__main__':
	app.run()