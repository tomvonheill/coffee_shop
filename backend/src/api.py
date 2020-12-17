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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all(app)

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
@requires_auth('get:drinks')
def get_drinks(payload):
    try:
        drinks = [drink.short() for drink in db.session.query(Drink)]
        if drinks:
            return json.dumps({'success':True, 'drinks': drinks})
        abort(404, description = 'No drinks found it database')
    except AuthError as e:
        abort(e.status_code, description = e.error)

@app.route('/test', methods = ['GET'])
@requires_auth('get:test')
def my_test(payload):
    try:
        print(payload)
        return 'access granted'
    except AuthError as e:
        abort(e.status_code, description = e.error)
    abort(500)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
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



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
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


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
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

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
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
'''
Example error handling for unprocessable entity
'''
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
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
