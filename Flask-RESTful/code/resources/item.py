import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', 
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'])

        try:
            item.create_item()
        except:
            return {"message": "An error occurred inserting the time."}, 500

        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_item()
            return {'message': "Item has been deleted"}
        return {'message': "Item doesn't exists"}, 500

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        updated_item = ItemModel(name, data['price'])
        
        if item is None:
            try:
                updated_item.create_item()
            except:
                return {"message": "An error occurred inserting the time."}, 500
        else:
            try:
                updated_item.update_item()
            except:
                return {"message": "An error occurred updating the time."}, 500

        return updated_item.json()


class ItemList(Resource):
    @classmethod
    def get_items(cls):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)

        items = []
        for row in result:
            items.append({'name': row[0], 'price': row[1]})

        connection.close()
        return items

    def get(self):
        items = self.get_items()
        return {'items': items}