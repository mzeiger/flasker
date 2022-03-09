from gettext import install
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
# pip install flask-sqlalchemy  Note the - in pip and the _ in import
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # note three ///


# Secret key
app.config['SECRET_KEY'] = "my secret key"

# Initialize the database
db = SQLAlchemy(app)

# Create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Name %r>' % self.name

# After saving above:
#    At bash terminal end flask with ^C
#    Enter "winpty python" to enter Python at terminal (winpty if using Git Bash)
#    Enter "from hello import db" (hello is app, db is db = SQLAlchemy(app))
#    Enter "db.create_all()"
#    Enter "exit()" to exit Python interpreter
#    Start flask again ("flask run")


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


# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create route and function
@app.route('/name', methods=['GET', 'POST']) 
def name():
    name = None
    form = NamerForm()
    # Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form submitted successfully')
    return render_template('name.html', name=name, form=form, the_title='Forms')

# Cretae a form class for the db
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form=UserForm()
    if form.validate_on_submit():
        # Users is the class that defined the database
        user = Users.query.filter_by(email=form.email.data).first()
        if user == None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash('User added successfully')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users, the_title='Database Entry')


