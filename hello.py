from flask import Flask, render_template


app = Flask(__name__)

# Create a route decorator

@app.route('/')
def index():
    return "<h1>Hello World, I'm Mark</h1>"

# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    return f"<h1>Hello {name}</h1>"
    # Could also be 
    #    return "<h1>Hello {}</h1>".format(name)

@app.route('/myindex/<my_name>')  # must start with '/'
def myindex(my_name):
    return render_template('index.html', v_name=my_name)
    # "v_name" variable is what is in the template as {{ v_name }}
    # "my_name" variable is what is in the URL as localhost:5000/myindex/xxx
    # In the "route" the variable must be in < >


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500



