#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )
        user.password_hash = json.get('password')
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            # db.session.rollback()
            return {'message': 'User already exists'}, 422
        
        

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        return {}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username==json['username']).first()
        if user and user.authenticate(json['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'message': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return {}, 204
        return {'message': 'No active session'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        user = User.query.filter(User.id == user_id).first()
        if user:
            recipes = [recipe.to_dict() for recipe in user.recipes]
            return recipes, 200
        return {'message': 'Unauthorized'}, 401

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        json = request.get_json()
        recipe = Recipe(
            title=json.get('title'),
            instructions=json.get('instructions'),
            minutes_to_complete=json.get('minutes_to_complete'),
            user_id=user_id
        )
        
        try:
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except IntegrityError:
            
            return {'message': 'Invalid recipe data'}, 422
        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
