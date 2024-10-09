from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', )

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Creating one-to-many relationship - a user can have many recipes
    recipes = db.relationship('Recipe', back_populates = 'user', cascade = 'all')

    @property
    def password(self):
        raise AttributeError('Not a readable attribute')
    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    serialize_rules = ('-user.recipes', )

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    instructions = db.Column(db.String, db.CheckConstraint('LENGTH(instructions) > 49'), nullable = False)
    minutes_to_complete = db.Column(db.Integer)
    
    # Foreign Key created on the many side to point to 1 user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relying solely on database constraints might not provide user-friendly error messages. Use the @validates decorator to enforce the minimum length at the instance level
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions)<=49:
            raise ValueError('Instructions must be at least 50 characters')
        return instructions

    # closing the loop of the one-to-many relationship
    user = db.relationship('User', back_populates='recipes')
