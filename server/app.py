#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Scientists(Resource):
    def get(self):
        scientists = [s.to_dict(rules=('-missions',)) for s in Scientist.query.all()]
        return make_response(jsonify(scientists), 200)

    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study')
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(jsonify(new_scientist.to_dict()), 201)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        return make_response(jsonify(scientist.to_dict()), 200)

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        
        data = request.get_json()
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.commit()
            return make_response(jsonify(scientist.to_dict()), 202)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        
        db.session.delete(scientist)
        db.session.commit()
        return make_response('', 204, {'Content-Type': 'application/json'})


class Planets(Resource):
    def get(self):
        planets = [p.to_dict(rules=('-missions',)) for p in Planet.query.all()]
        return make_response(jsonify(planets), 200)


class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(
                name=data.get('name'),
                scientist_id=data.get('scientist_id'),
                planet_id=data.get('planet_id')
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(jsonify(new_mission.to_dict()), 201)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')


@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
