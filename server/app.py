# app.py

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError, OperationalError # Import OperationalError for db issues
from models import db, Author, Post # Import your models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # Database will be in the server directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# --- Custom Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    message = str(error) if isinstance(error, Exception) else "Resource not found"
    return make_response(jsonify({"error": message}), 404)

@app.errorhandler(400)
def bad_request(error):
    message = str(error) if isinstance(error, Exception) else "Bad Request"
    return make_response(jsonify({"error": message}), 400)

@app.errorhandler(500)
def internal_server_error(error):
    message = str(error) if isinstance(error, Exception) else "Internal Server Error"
    return make_response(jsonify({"error": message}), 500)

# --- Routes ---

@app.route('/')
def index():
    return '<h1>Flask-SQLAlchemy Validations Lab API</h1>'

# --- Author Routes ---

# GET /authors: Get all authors
@app.route('/authors', methods=['GET'])
def get_authors():
    try:
        authors = Author.query.all()
        return make_response(jsonify([author.to_dict() for author in authors]), 200)
    except Exception as e:
        db.session.rollback()
        return internal_server_error(str(e))

# GET /authors/<int:id>: Get a single author by ID
@app.route('/authors/<int:id>', methods=['GET'])
def get_author_by_id(id):
    author = Author.query.get(id)
    if not author:
        return not_found(f"Author with id {id} not found.")
    try:
        return make_response(jsonify(author.to_dict()), 200)
    except Exception as e:
        return internal_server_error(str(e))

# POST /authors: Create a new author (will trigger validations)
@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    if not data:
        return bad_request("No input data provided.")

    try:
        new_author = Author(
            name=data.get('name'),
            phone_number=data.get('phone_number')
        )
        db.session.add(new_author)
        db.session.commit()
        return make_response(jsonify(new_author.to_dict()), 201)
    except ValueError as e: # Catch validation errors from @validates
        db.session.rollback()
        return bad_request(str(e))
    except IntegrityError: # Catch unique constraint violations (e.g., duplicate name)
        db.session.rollback()
        return bad_request("Author with this name already exists.")
    except Exception as e:
        db.session.rollback()
        return internal_server_error(str(e))

# --- Post Routes ---

# GET /posts: Get all posts
@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = Post.query.all()
        return make_response(jsonify([post.to_dict() for post in posts]), 200)
    except Exception as e:
        db.session.rollback()
        return internal_server_error(str(e))

# GET /posts/<int:id>: Get a single post by ID
@app.route('/posts/<int:id>', methods=['GET'])
def get_post_by_id(id):
    post = Post.query.get(id)
    if not post:
        return not_found(f"Post with id {id} not found.")
    try:
        return make_response(jsonify(post.to_dict()), 200)
    except Exception as e:
        return internal_server_error(str(e))

# POST /posts: Create a new post (will trigger validations)
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data:
        return bad_request("No input data provided.")

    try:
        new_post = Post(
            title=data.get('title'),
            content=data.get('content'),
            summary=data.get('summary'),
            category=data.get('category'),
            author_id=data.get('author_id')
        )
        db.session.add(new_post)
        db.session.commit()
        return make_response(jsonify(new_post.to_dict()), 201)
    except ValueError as e: # Catch validation errors from @validates
        db.session.rollback()
        return bad_request(str(e))
    except IntegrityError: # Catch foreign key or other integrity errors
        db.session.rollback()
        return bad_request("Failed to create post. Ensure author_id is valid.")
    except Exception as e:
        db.session.rollback()
        return internal_server_error(str(e))

if __name__ == '__main__':
    # Ensure tables are created if running app.py directly without full migrations
    # This is helpful for quick local testing and development.
    with app.app_context():
        db.create_all() 
    app.run(port=5555, debug=True)

