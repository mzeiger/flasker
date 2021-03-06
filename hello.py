from gettext import install
from hashlib import sha256
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField,ValidationError
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length, InputRequired
# pip install flask-sqlalchemy  Note the - in pip and the _ in import
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


app = Flask(__name__)

# Add sqlite database
# commented out to implement mySQL database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # note three ///

# This is for mySQL. It's 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://<user name><password>@<host>/<db_name'
# need to install:
#     pip install pymysql
#     pip install cryptography
# Then we can run using 'winpty python'
#      from hello import db
#      db.create_all()
#      exit()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mzeiger:Tango_32@localhost/sql_users'

# Secret key
app.config['SECRET_KEY'] = "my secret key"

# Initialize the database
db = SQLAlchemy(app)
migrate=Migrate(app, db)  # added to make flask db migrate -m "<some message>" ' work 

# Create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Name %r>' % self.name

    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# After saving above:
#    At bash terminal end flask with ^C
#    Enter "winpty python" to enter Python at terminal (winpty if using Git Bash)
#    Enter "from hello import db" (hello is app, db is db = SQLAlchemy(app))
#    Enter "db.create_all()"
#    Enter "exit()" to exit Python interpreter
#    Start flask again ("flask run")

# If the database structure needs to up updated
#   In terminal ^C out of flask
#   Enter command 'flask db migrate -m "<some message>" '
#       Note: Needed to add migrate=Migrate(app, db)  under db = SQLAlchemy(app)
#   Enter command 'db upgrade'


favorite_pizza = ['Pepperroni', 'Cheese', 'Mushroom', 4]
# Create a route decorator

@app.route('/')
def index():
    return render_template('index.html', pizza=favorite_pizza, the_title='Codemy.com')

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
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired(), Email(message='Invalid email')])
    password_hash = PasswordField("What is your password", validators=[InputRequired()])
    submit = SubmitField('Submit')

# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create password test page
@app.route('/test_pw', methods=['GET', 'POST']) 
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate form

    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        if pw_to_check == None:
            return render_template('test_pw.html', record_not_found=True, email=email)
        # Check hashed passwork
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password_hash=password, 
                             pw_to_check=pw_to_check, record_not_found=False,
                             passed = passed, form=form, the_title='Password Check')



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
    name = StringField("Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password_hash = PasswordField('Password', validators=[InputRequired(), 
                    EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField('Comfrim Password', validators=[InputRequired()])
    submit = SubmitField('Add User')



@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    user_added = ''
    form=UserForm()
    flash_msg = ''
    if form.validate_on_submit():
        # Users is the class that defined the database
        user = Users.query.filter_by(email=form.email.data.lower()).first()
        if user == None:
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name=form.name.data, email=form.email.data.lower(), password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            user_added = True
            flash_msg = f'{form.name.data} at {form.email.data} added successfully'
            # flash(f'{form.name.data} at {form.email.data} added successfully')
        else:
            flash_msg = f'A user with the email {user.email} is already in the database'
            user_added = False
           # flash(f'A user with the email {user.email} is already in the database')
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
    our_users = Users.query.order_by(Users.date_added)
    #if user_added:
    #   flash(f'{form.name.data} at {form.email.data} added successfully')
    #else:
    #    flash(f'A user with the email {user.email} is already in the database')
    flash(flash_msg)
    return render_template('add_user.html', form=form, name=name, 
         our_users=our_users, user_added=user_added, the_title='Database Entry')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    original_name = name_to_update.name
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            users = Users.query.order_by(Users.date_added)
            flash(f'User {original_name} updated sucessfully')
            return render_template('update.html', form=form,  
                              our_users= users, was_posted = True, the_title='Update')
        except:
            users = Users.query.order_by(Users.date_added)
            flash(f'ERROR: User {name_to_update} update failed... try again')
            return render_template('update.html', form=form, our_users=users, 
                        name_to_update=name_to_update, the_title='Update')
    else:        
        users = Users.query.order_by(Users.date_added)
        return render_template('update.html', form=form, our_users=users, 
                        name_to_update=name_to_update, was_posted=False, the_title='Update')


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    form = UserForm()
    name = None

    user_to_delete = Users.query.get_or_404(id)
    original_name = user_to_delete.name
    db.session.delete(user_to_delete)
    try:
        db.session.commit()
        users = Users.query.order_by(Users.date_added)
        flash(f'User {original_name} deleted sucessfully')
        return render_template('add_user.html', form=form, our_users=users, the_title='Add User')
    except:
        flash(f'ERROR: User {user_to_delete} deletion failed... try again')
        users = Users.query.order_by(Users.date_added)
    
        return render_template('add_user.html', form=form, our_users=users, the_title='Add User')

        


