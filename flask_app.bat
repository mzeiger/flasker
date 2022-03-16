from flask import Flask


app = Flask(__name__)
posts = {
    0: {
        'title': 'Hello, world',
        'content': 'This is my first blog post'
    },
    1: {
        'title': 'Goodbye World',
        'content': 'This is my second blog'
    }
}


@app.route('/')
def home():
    return '<h1>Hello world</h1>'


@app.route('/post/<int:post_id>')   # flask syntax for post/0
def post(post_id):
    my_post = posts.get(post_id)
    return f"Post Title: {my_post['title']}, <br/>Content: {my_post['content']}"


if __name__ == '__main__':
    app.run(debug=True)

