from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin # Import SerializerMixin
import re # Import regex for phone number validation

db = SQLAlchemy()

class Author(db.Model, SerializerMixin): # Add SerializerMixin
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False) # All authors have a name, No two authors have the same name.
    phone_number = db.Column(db.String) # Author phone numbers are exactly ten digits.
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Define a one-to-many relationship with Post
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

    # Serialization rules to avoid circular references if needed
    serialize_rules = ('-posts.author',)

    # Add validators 
    @validates('name')
    def validate_name(self, key, name):
        # All authors have a name (already handled by nullable=False)
        # No two authors have the same name (already handled by unique=True)
        if not name:
            raise ValueError("Author must have a name.")
        return name

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        # Author phone numbers are exactly ten digits.
        if phone_number is None: # Allow phone_number to be None if it's not required
            return phone_number
        # Use regex to check for exactly 10 digits
        if not re.fullmatch(r'\d{10}', phone_number):
            raise ValueError("Phone number must be exactly ten digits.")
        return phone_number

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'

class Post(db.Model, SerializerMixin): # Add SerializerMixin
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False) # Post title is sufficiently clickbait-y
    content = db.Column(db.String) # Post content is at least 250 characters long.
    category = db.Column(db.String) # Post category is either Fiction or Non-Fiction.
    summary = db.Column(db.String) # Post summary is a maximum of 250 characters.
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Define a many-to-one relationship with Author
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Serialization rules
    serialize_rules = ('-author.posts',)

    # Add validators 
    @validates('content')
    def validate_content(self, key, content):
        # Post content is at least 250 characters long.
        if not content or len(content) < 250:
            raise ValueError("Post content must be at least 250 characters long.")
        return content

    @validates('summary')
    def validate_summary(self, key, summary):
        # Post summary is a maximum of 250 characters.
        if summary and len(summary) > 250:
            raise ValueError("Post summary cannot exceed 250 characters.")
        return summary

    @validates('category')
    def validate_category(self, key, category):
        # Post category is either Fiction or Non-Fiction.
        if category not in ['Fiction', 'Non-Fiction']:
            raise ValueError("Post category must be 'Fiction' or 'Non-Fiction'.")
        return category

    @validates('title')
    def validate_title(self, key, title):
        # Post title is sufficiently clickbait-y and must contain one of the following:
        # "Won't Believe", "Secret", "Top", "Guess"
        clickbait_keywords = ["Won't Believe", "Secret", "Top", "Guess"]
        if not any(keyword in title for keyword in clickbait_keywords):
            raise ValueError("Post title must contain one of: 'Won't Believe', 'Secret', 'Top', 'Guess'.")
        return title

    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
