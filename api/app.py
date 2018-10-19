"""!Flask web api for Store Manager"""
from flask import Flask, jsonify, abort, make_response, request

NOT_FOUND = 'Not found'
BAD_REQUEST = 'Bad request'

app = Flask(__name__)
"""initializing"""

PRODUCTS = [
    {
        'product_id': 1,
        'product_name': 'Sugar',
        'category': 'Food',
        'unit_price': 4000,
        'quantity' : '100',
        'measure' : 'Kg'
    },
    {
        'product_id': 2,
        'product_name': 'Ariel-Small',
        'category': 'Detergent',
        'unit_price': 500,
        'quantity' : '40',
        'measure' : 'Pkts'
    },
    {
        'product_id': 3,
        'product_name': 'Ariel-Big',
        'category': 'Detergent',
        'unit_price': 2000,
        'quantity' : '35',
        'measure': 'Pkts'
    },
    {
        'product_id': 4,
        'product_name': 'Broom',
        'category': 'Home Utilities',
        'unit_price': 1000,
        'quantity' : '10',
        'measure': 'Sticks'
    },
    {
        'product_id': 5,
        'product_name': '98-Paged Picfare Books',
        'category': 'Scholastic Materials',
        'unit_price': 4800,
        'quantity' : '144',
        'measure': 'Dozens'
    },
    {
        'product_id': 6,
        'product_name': 'Bic Pens',
        'category': 'Scholastic Materials',
        'unit_price': 5000,
        'quantity' : '12',
        'measure': 'Box'
    },
    {
        'product_id': 6,
        'product_name': 'Vanilla Sponge Cake',
        'category': 'Baked Goodies',
        'unit_price': 7500,
        'quantity' : '3',
        'measure': 'Slices'
    },
    {
        'product_id': 7,
        'product_name': 'Always',
        'category': 'Women Products',
        'unit_price': 3000,
        'quantity' : '12',
        'measure': 'Pkts'
    },
    {
        'product_id': 8,
        'product_name': 'Vaseline Cocoa',
        'category': 'Women Products',
        'unit_price': 12000,
        'quantity' : '10',
        'measure': 'Bottles'
    },
    {
        'product_id': 9,
        'product_name': 'Vaseline Cocoa',
        'category': 'Men Products',
        'unit_price': 12000,
        'quantity' : '10',
        'measure': 'Bottles'
    },
    {
        'product_id': 10,
        'product_name': 'Vaseline Men',
        'category': 'Men Products',
        'unit_price': 10000,
        'quantity' : '10',
        'measure': 'Bottles'
    },
    {
        'product_id': 11,
        'product_name': 'Zesta Strawberry Jam',
        'category': 'Food',
        'unit_price': 7500,
        'quantity' : '5',
        'measure': 'Bottles'
    }
]
SALES = [
    {
        'product_id': 1,
        'sale_id': 1,
        'product_name': 'Sugar',
        'quantity': '2',
        'date': '2018-10-10',
        'price': '8000',
        'payment': 'cash',
        'attendant': 'johnny'

    },
    {
        'product_id': 1,
        'sale_id': 2,
        'product_name': 'Sugar',
        'quantity': '1',
        'date': '2018-10-12',
        'price': '4000',
        'payment': 'cash',
        'attendant': 'tom'

    },
    {
        'product_id': 6,
        'sale_id': 3,
        'product_name': 'Bic Pens',
        'quantity': '3',
        'date': '2018-10-10',
        'price': '15000',
        'payment': 'cash',
        'attendant': 'johnny'

    }
]

@app.route('/')
def hello():
    """my first home"""
    return jsonify({"Hello Welcome to Store Manager API": "navigate with storemanager\api\v1"})

#other methods
def _get_product(productid):
    """_get_product(productid) returns a product in products via product_id"""
    return [product for product in PRODUCTS if product['product_id'] == productid]

def _record_exists(productname):
    """_record_exists(productname) returns a product in products via product_name"""
    return [product for product in PRODUCTS if product["product_name"] == productname]

def _record_exists_(productid):
    """_record_exists(productid) returns a product in products via product_id"""
    return [product for product in PRODUCTS if product["product_id"] == productid]

def _record_exist_(saleid):
    """_record_exist(saleid) returns a sale in sales via sale_id"""
    return [sale for sale in SALES if sale["sale_id"] == saleid]

#get all products
@app.route('/storemanager/api/v1/products', methods=['GET'])
def get_products():
    """get_products() -- returns all products"""
    return jsonify({'products': PRODUCTS})

#get specific product
@app.route('/storemanager/api/v1/products/<int:_id>', methods=['GET'])
def get_product(_id):
    """get_product(_id) -- returns a product via its id"""
    _product_ = _get_product(_id)
    if not _product_:
        abort(404)
    return jsonify({'product': _product_})

#post a product
@app.route('/storemanager/api/v1/products', methods=['POST'])
def create_product():
    """create_product() --returns a product that has been added"""
    prod_id = request.get_json('product_id')
    prod_name = request.get_json('product_name')
    prod_cat = request.get_json('category')
    prod_price = request.get_json('unit_price')
    prod_qty = request.get_json('quantity')
    prod_meas = request.get_json('measure')

    if _record_exists(prod_name):
        abort(400)
    elif _record_exists_(prod_id):
        abort(400)
    else:
        _product = {
            'product_id':prod_id,
            'product_name':prod_name,
            'category':prod_cat,
            'unit_price':prod_price,
            'quantity':prod_qty,
            'measure':prod_meas
        }
        PRODUCTS.append(_product)
        return jsonify({"Success":"product '{0}' added".format(_product["product_name"])}), 201

#delete a product
@app.route('/storemanager/api/v1/products/<int:_id>', methods=['DELETE'])
def delete_product(_id):
    """delete_product(_id)--deletes product"""
    prod_ = _get_product(_id)
    PRODUCTS.remove(prod_[0])
    return "Successfully deleted it", 204

#add a sale
@app.route('/storemanager/api/v1/sales', methods=['POST'])
def create_sale():
    """create_sale() --returns a product that has been added"""
    sale_id = request.get_json('sale_id')
    prod_id = request.get_json('product_id')
    prod_name = request.get_json('product_name')
    price_ = request.get_json('price')
    date_ = request.get_json('date')
    prod_qty = request.get_json('quantity')
    payment_ = request.get_json('payment')
    attendant_ = request.get_json('attendant')

    if _record_exist_(sale_id):
        abort(400)
    else:
        _sale = {
            'sale_id':sale_id,
            'product_id':prod_id,
            'product_name':prod_name,
            'price':price_,
            'date':date_,
            'quantity':prod_qty,
            'payment':payment_,
            'attendany': attendant_
        }
        SALES.append(_sale)
        return jsonify({"Success":"slae '{0}' added".format(_sale["sale_id"])}), 201

#get all sales
@app.route('/storemanager/api/v1/sales', methods=['GET'])
def get_sales():
    """get_sales() -- returns all sales"""
    return jsonify({'sales': SALES})

if __name__ == '__main__':
    app.run(debug=True)
