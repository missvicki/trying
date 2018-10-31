"""!Flask web api for Store Manager"""
from flask import Flask, jsonify, abort, make_response, request
import datetime
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from werkzeug.security import check_password_hash, generate_password_hash
from model import DatabaseConnection
from db import Products, Sales, Users, Login, SalesHasProducts

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'secret'
jwt = JWTManager(app)

database = DatabaseConnection()
database.drop_tables()
database.create_tables()
database.default_admin()

#error handlers
@app.errorhandler(404)
def not_found(error):
    """ not_found(error) -returns error not found"""
    return make_response(jsonify({'error': 'NOT FOUND'}), 404)

@app.errorhandler(400)
def bad_request(error):
    """ bad_request(error) -returns error bad request"""
    return make_response(jsonify({'error': 'BAD REQUEST'}), 400)

@app.errorhandler(405)
def mtd_not_allowed(error):
    """ mtd_not_allowed(error) -returns error method not allowed"""
    return make_response(jsonify({'error': "METHOD NOT ALLOWED"}), 405)

@app.errorhandler(401)
def unauthorized(error):
    """ unauthorized(error) -returns error unauthorized"""
    return make_response(jsonify({'error': "NOT AUTHORIZED"}), 401)

@app.route('/')
def hello():
    """my home"""
    return "Hello Welcome to Store Manager API"

@app.route('/api/v1/products', methods=['GET', 'POST'])
def products():
    """returns all products"""
    if request.method == 'GET':
            productget = database.getProducts()
            if productget:
                return jsonify({'products': productget}), 200
            else:
                return jsonify({'message': "There are no products"}), 404
  
    if request.method == 'POST':
            """returns a product that has been added"""
            data = request.get_json()
            prod_name = data.get('product_name')
            prod_cat = data.get('category')
            prod_price = data.get('unit_price')
            prod_qty = data.get('quantity')
            prod_meas = data.get('measure')
            

            # check if product exists
            data_product_name_exist = database.check_product_exists_name(prod_name)
            if not data:
                return jsonify({'message': "Missing json request"}), 400
            elif not prod_name or not prod_cat or not prod_price or not prod_qty or not prod_meas:
                return jsonify({'message': "Fields can't be empty"}), 400
            elif not isinstance(prod_price, int) or not isinstance(prod_qty, int):
                return jsonify({'message': "Price and Quantity have to be integers"}), 400
            elif data_product_name_exist:
                return jsonify({'message': "Product already exists"}), 400
            else:
                obj_products = Products(prod_name, prod_cat, prod_price, prod_qty, prod_meas)
                database.insert_data_products(obj_products)
                return jsonify({"Success": "product has been added"}), 201
    else:
        abort(405)

# get specific product and delete a product and modify product
@app.route('/api/v1/products/<int:_id>', methods=['GET','DELETE', 'PUT'])
@jwt_required
def _product_(_id):
    current_user = get_jwt_identity()
    if request.method == 'GET':
        """returns a product via its id"""
        if current_user == 'admin' or current_user == 'attendant':
            _product_ = database.getoneProduct(_id)
            if _product_:
                return jsonify({'product': _product_}), 200
            else:
                return jsonify({'product': "product has not been found"}), 404
        else:
            return jsonify({'message': "You are not authorized"}), 401
    elif request.method == 'DELETE':
        """delete_product(_id)--deletes product"""
        if current_user == 'admin':
            del_prod = database.check_product_exists_id(_id)
            if not del_prod:
                return jsonify({"error": "Product your are trying to delete does not exist"}), 404
            else:
                database.deloneProduct(_id)
                return jsonify({"message": "Product has been deleted successfully"}), 200
        else:
            return jsonify({'message': "You are unauthorized"}), 401
    elif request.method == 'PUT':
        """put product"""
        if current_user == 'admin':
            prod = database.check_product_exists_id(_id)
            if not prod:
                return jsonify({"error": "product you are trying to modify does not exist"}), 404
            else:
                data = data = request.get_json()
                prod_name = data.get('product_name')
                prod_cat = data.get('category')
                prod_price = data.get('unit_price')
                prod_qty = data.get('quantity')
                prod_meas = data.get('measure')
                if not data:
                    return jsonify({'message': "Missing json request"}), 400
                elif not prod_name or not prod_cat or not prod_price or not prod_qty or not prod_meas:
                    return jsonify({'message': "Fields can't be empty"}), 400
                elif not isinstance(prod_price, int) or not isinstance(prod_qty, int):
                    return jsonify({'message': "Price and Quantity have to be integers"}), 400
                else:
                    database.modify_product(prod_name, prod_cat, prod_price, prod_qty, prod_meas, _id)
                    return jsonify({"Success": "product has been modified"}), 201
        else:
            return jsonify({"message": "You are not authorized"}), 401
    else:
        abort(405)  

#get users
@app.route('/api/v1/users', methods=['GET'])
@jwt_required
def _users_():
    """returns all users"""
    current_user = get_jwt_identity()
    if current_user == 'admin':
        if request.method == 'GET':
            userget = database.getUsers()
            if userget:
                return jsonify({'users': userget}), 200
            else:
                return jsonify({'message': "There are no users"}), 404
    else:
        return jsonify({"message": "You are not authorized"}), 401

# create user auth
@app.route('/api/v1/auth/signup', methods=['POST'])
@jwt_required
def signup():
        """returns a user that has been added"""
        current_user = get_jwt_identity()
        if current_user == 'admin':
            if request.method == 'POST':
                data = request.get_json()
                name = data.get('name')
                user_name = data.get('user_name')
                password = data.get('password')
                role = data.get('role')
                # check if user exists
                data_user_name_exist = database.check_user_exists_name(user_name)
                data_user_pass_exist = database.check_user_exists_password(password)
                if not data:
                    return jsonify({'message': "Missing json request"}), 400
                elif not name or not user_name or not password or not role:
                    return jsonify({'message': "Fields can't be empty"}), 400
                elif data_user_name_exist:
                    return jsonify({'error': "user name already exists"}), 400
                elif data_user_pass_exist:
                    return jsonify({'error': "try another password-that one may have been used"}), 400
                else:
                    obj_users = Users(name, user_name, password, role)
                    database.insert_table_users(obj_users)
                    return jsonify({"Success": "user has been added"}), 201
            else:
                return jsonify({"message": "Method not allowed"}), 405
        else:
            return jsonify({"message": "You are not authorized"}), 401
# user login
# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    if request.method == 'POST':
        """returns a user login"""
        data = request.get_json()
        user_name = data.get('user_name')
        password = data.get('password')
        role = data.get('role')

        data_user_name_exist = database.check_user_exists_name(user_name)
        data_user_pass_exist = database.check_user_exists_password(password)
        data_user_role_exist = database.check_user_exists_role(role, user_name)
        if not data:
            return jsonify({'message': "Missing json request"}), 400
        elif not user_name or not password or not role:
            return jsonify({'message': "Missing username or password"}), 400
        elif not data_user_name_exist:
            return jsonify({'error': "user name does not exist, sign up first"}), 400
        elif not data_user_pass_exist:
            return jsonify({'error': "invalid password"}), 400
        elif not data_user_role_exist:
            return jsonify({'error': "invalid role"}), 400
        else:
            # Identity can be any data that is json serializable
            
            obj_login = Login(user_name, password, role)
            database.insert_table_login(obj_login)
            access_token = create_access_token(identity=role, expires_delta=datetime.timedelta(days=100))
            return jsonify(access_token="Bearer {}".format(access_token)), 200
            # return jsonify({"Success": "user has been logged in"}), 201
    else:
        abort(405)

#delete modify users
# get specific product and delete a product and modify product
@app.route('/api/v1/users/<int:_id>', methods=['GET','DELETE', 'PUT'])
@jwt_required
def _user_(_id):
    current_user = get_jwt_identity()
    if request.method == 'GET':
        """returns a user via its id"""
        if current_user == 'admin':
            _user_ = database.getoneUser(_id)
            if _user_:
                return jsonify({'user': _user_}), 200
            else:
                return jsonify({'user': "user has not been found"}), 404
        else:
            return jsonify({"message": "You are not authorized"}), 401
    elif request.method == 'DELETE':
        """delete_user(_id)--deletes user"""
        if current_user == 'admin':
            del_user = database.check_user_exists_id(_id)
            if not del_user:
                return jsonify({"error": "user your are trying to delete does not exist"}), 404
            else:
                database.deloneuser(_id)
                return jsonify({"message": "user has been deleted successfully"}), 200
        else:
            return jsonify({"message": "You are not authorized"}), 401
    elif request.method == 'PUT':
        """put user"""
        if current_user == 'admin':
            u = database.check_user_exists_id(_id)
            if not u:
                return jsonify({"error": "user you are trying to modify does not exist"}), 404
            else:
                data = data = request.get_json()
                name = data.get('name')
                user_name = data.get('user_name')
                password = data.get('password')
                role = data.get('role')
                if not data:
                    return jsonify({'message': "Missing json request"}), 400
                elif not name or not user_name or not password or not role:
                    return jsonify({'message': "Fields can't be empty"}), 400
                else:
                    database.modify_user(name, user_name, password, role, _id)
                    return jsonify({"Success": "user has been modified"}), 201
        else:
            return jsonify({"message": "You are not authorized"}), 401
    else:
        abort(405)  

#add a sale
@app.route('/api/v1/sales', methods=['GET','POST'])
@jwt_required
def _sale():
    """_sale() """
    current_user = get_jwt_identity()
    if request.method == 'GET':
        if current_user == 'admin' or current_user == 'attendant':
            saleget = database.getsales()
            if saleget:
                return jsonify({'sales': saleget}), 200
            else:
                return jsonify({'message': "There are no sales"}), 404
        else:
            return jsonify({"message": "You are not authorized"}), 401
    elif request.method == 'POST':
        """add sales"""
        if current_user == 'attendant':
            data = request.get_json()
            user_id = int(data.get('user_id'))
            quantity = int(data.get('quantity'))
            product_id = int(data.get('product_id'))

            # get quantity
            getQty = int(database.getQuantity(product_id))
            # get unit price
            getPrice = int(database.getPrice(product_id))
            # calculate total
            total = quantity * getPrice
            # new qty
            newqty = getQty - quantity
            # check empty fields
            if not data:
                return jsonify({'message': "Missing json request"}), 400
            elif not user_id or not quantity or not product_id or not total:
                return jsonify({'message': "Fields can't be empty"}), 400
            # validate integers
            elif not isinstance(user_id, int) or not isinstance(quantity, int) or not isinstance(product_id, int) or not isinstance(getQty, int):
                return jsonify({'message': "fields have to be integers"}), 400
            else:
                obj_sales = Sales(user_id)
                database.insert_data_sales(obj_sales)
                obj_salepdt = SalesHasProducts(product_id, quantity, total)
                database.insert_data_saleshasproducts(obj_salepdt)
                return jsonify({"Success": "user has been added"}), 201
        else:
            return jsonify({"message": "You are not authorized"}), 401
    else:
        abort(405)

if __name__ == '__main__':
    app.run(debug=True)