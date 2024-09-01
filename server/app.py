#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries', methods= ['GET','POST'])
def bakeries():
    if request.method =='GET':
     bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
     return make_response(  bakeries,   200  )
    
        # POST block: creates a new baked good
    elif request.method == 'POST':
        data = request.form
        new_baked_good = BakedGood(
            name=data.get('name'),
            price=float(data.get('price')),
            bakery_id=int(data.get('bakery_id'))
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(jsonify(new_baked_good.to_dict()), 201)

# GET /bakeries/<int:id>: returns a single bakery as JSON
# PATCH /bakeries/<int:id>: updates the bakery name
@app.route('/bakeries/<int:id>', methods=['GET','PATCH'])
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()

    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found'}), 404)
    
    if request.method == 'GET':
     bakery_serialized = bakery.to_dict()
     return make_response ( bakery_serialized, 200  )

    # PATCH block: updates the bakery name
    elif request.method == 'PATCH':
        data = request.form
        bakery.name = data.get('name', bakery.name)  # Updates only if 'name' is provided
        db.session.commit()
        return make_response(jsonify(bakery.to_dict()), 200)

# GET /baked_goods/by_price: returns baked goods sorted by price in descending order 
@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(jsonify(baked_goods_by_price_serialized), 200)
   
# GET /baked_goods/most_expensive: returns the most expensive baked good
@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if most_expensive:
        return make_response(jsonify(most_expensive.to_dict()), 200)
    return make_response(jsonify({'error': 'No baked goods found'}), 404)

# DELETE /baked_goods/<int:id>: deletes a baked good and returns a confirmation message
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()

    if not baked_good:
        return make_response(jsonify({'error': 'Baked good not found'}), 404)

    db.session.delete(baked_good)
    db.session.commit()
    return make_response(jsonify({'message': 'Baked good successfully deleted'}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)