#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username and not password:
            return {'Error':'username and password must be submitted'}, 400
        
        user = User()
        for field in ['username', 'image_url', 'bio', 'password']:
            setattr(user, field, data.get(field))

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {'Error': 'username already exists'}, 422


# Handles auto-login for time users refresh the page or navigate back to the site from elsewhere.
class CheckSession(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {'Error': 'Unauthorized'}, 401

class Login(Resource):
    
    def post(self):
        user = User.query.filter(User.username == request.get_json().get('username')).first()
        if user and user.authenticate(request.get_json().get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'Error':'Incorrect Username or password'}, 401


class Logout(Resource):
    
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        else:
            return {'Error': 'User not logged in'}, 401

class RecipeIndex(Resource):
    
    def get(self):
        if session.get('user_id'):
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
            return recipes, 200
        else:
            return {'Error': 'Please Log In to view recipes'}, 401
    
    def post(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'Error':'Must be signed in'}, 401
        
        data = request.get_json()
        try:
            recipe = Recipe()
            for field in ['title', 'instructions', 'minutes_to_complete']:
                setattr(recipe, field, data.get(field))
            recipe.user_id = user_id  # Move outside the loop
            
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except ValueError as ve:
            db.session.rollback()
            return {'error': str(ve)}, 422



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)