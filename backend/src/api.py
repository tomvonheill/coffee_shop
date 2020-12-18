import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)
db_drop_and_create_all(app)

## ROUTES
@app.route('/drinks', methods = ['GET'])
def get_drinks():
    drinks = [drink.short() for drink in db.session.query(Drink)]
    if drinks:
        return json.dumps({'success':True, 'drinks': drinks})
    abort(404, description = 'No drinks found it database')

@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = [drink.long() for drink in db.session.query(Drink)]
        if drinks:
            return json.dumps({'success':True, 'drinks': drinks})
        abort(404, description = 'No drinks found it database')
    except AuthError as e:
        abort(e.status_code, description = e.error)

@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    title = request.get_json().get('title')
    recipe = request.get_json().get('recipe')
    if not title:
        abort(400, description = 'No title was given to new drink')
    if len(recipe)<1:
        abort(400, description= 'No recipe was given')
    drink = Drink(title=title,recipe=json.dumps(recipe))
    drink.insert()
    return json.dumps({'success': True, 'drink': drink.long()})

@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    recipe = request.get_json().get('recipe', [])
    title = request.get_json().get('title', '')
    if not id:
        abort(400, description = 'No id given')

    drink = Drink.query.get(id)
    if not drink:
        abort(404, description=f'No drink of id {id}')
    
    drink.title = title
    drink.recipe = json.dumps(recipe)
    drink.update()
    return json.dumps({'success': True, 'drinks': [drink.long()]})

@app.route('/drinks/<int:id>', methods = ['delete'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404, description=f'No drink of id {id}')
    
    drink.delete()
    drink.update()
    return json.dumps({'success': True, 'delete':id})


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def questions_not_found(error):
    error_data = {
        'success' : False,
        'error' : 404,}
    error_data['message'] =error.description
    return jsonify(error_data),404

@app.errorhandler(400)
def questions_not_found(error):
    error_data = {
        'success' : False,
        'error' : 404,}
    error_data['message'] =error.description
    return jsonify(error_data),404

@app.errorhandler(AuthError)
def questions_not_found(error):
    error_data = {
        'success' : False,
        'error' : error.status_code,}
    error_data['message'] =error.error
    return jsonify(error_data),error.status_code
