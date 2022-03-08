from gettext import install
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config['SECRET_KEY'] = "my secret key"
# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField('Submit')

favorite_pizza = ['Pepperroni', 'Cheese', 'Mushroom', 4]
# Create a route decorator

@app.route('/')
def index():
    return render_template('index.html', pizza=favorite_pizza, the_title='Pizza')

# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    if name == None:
        name = 'Anybody'
    return f"<h1>Hello {name}</h1>"
    # Could also be 
    #    return "<h1>Hello {}</h1>".format(name)

@app.route('/myindex/<my_name>')  # must start with '/'
def myindex(my_name):
    return render_template('index.html', v_name=my_name, the_title=my_name, pizza=favorite_pizza)
    # "v_name" variable is what is in the template as {{ v_name }}
    # "my_name" variable is what is in the URL as localhost:5000/myindex/xxx
    # In the "route" the variable must be in < >


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', the_title='404 Error'), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', the_title='500 Error'), 500


# Create route and function
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('name.html', name=name, form=form, the_title='Forms')



