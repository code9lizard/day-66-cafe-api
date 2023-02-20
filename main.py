from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import random


def get_cafe_list():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    all_cafes_list = []
    for chosen_cafe in all_cafes:
        cafe_data = jsonify(can_take_calls=chosen_cafe.can_take_calls,
                            coffee_price=chosen_cafe.coffee_price,
                            has_sockets=chosen_cafe.has_sockets,
                            has_toilet=chosen_cafe.has_toilet,
                            has_wifi=chosen_cafe.has_wifi,
                            id=chosen_cafe.id,
                            img_url=chosen_cafe.img_url,
                            location=chosen_cafe.location,
                            map_url=chosen_cafe.map_url,
                            name=chosen_cafe.name,
                            seats=chosen_cafe.seats).json
        all_cafes_list.append(cafe_data)
    return jsonify(cafe=all_cafes_list).json


def check_key(api_key):
    if api_key == "TOPSECRETAPIKEY":
        return True
    else:
        return False


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/random", methods=["GET"])
def get_random_cafe():
    json_data = get_cafe_list()
    all_cafes_list = json_data["cafe"]
    num_of_cafes = len(all_cafes_list)
    random_id = random.randint(1, num_of_cafes)
    for cafe in json_data["cafe"]:
        if cafe["id"] == random_id:
            return cafe


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all")
def get_all_cafes():
    json_data = get_cafe_list()
    return json_data


@app.route("/search")
def search_cafes():
    json_data = get_cafe_list()
    location = request.args.get("loc").title()
    nearest_cafe = [cafe for cafe in json_data["cafe"] if cafe["location"] == location]
    return nearest_cafe


@app.route("/add", methods=["POST"])
def add_cafe():
    key = request.headers.get("api-key")
    if check_key(key):
        new_cafe = Cafe(name=request.values.get("name"),
                        location=request.values.get("location"),
                        has_sockets=bool(request.values.get("has_sockets")),
                        img_url=request.values.get("img_url"),
                        map_url=request.values.get("map_url"),
                        coffee_price=request.values.get("coffee_price"),
                        seats=request.values.get("seats"),
                        can_take_calls=bool(request.values.get("can_take_calls")),
                        has_wifi=bool(request.values.get("has_wifi")),
                        has_toilet=bool(request.values.get("has_toilet")))
        db.session.add(new_cafe)
        db.session.commit()
        response = jsonify(response={"success": f"Successfully added {new_cafe.name}."})
        return response
    response = jsonify(error={"Forbidden": "Sorry that's not allowed. Make sure you have the correct api_key."})
    return response, 403


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    chosen_cafe = db.session.execute(db.select(Cafe).filter_by(id=cafe_id)).scalar_one_or_none()
    new_price = request.args.get("new_price")
    if chosen_cafe is None:
        response = jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})
        return response, 404
    chosen_cafe.coffee_price = new_price
    db.session.commit()
    response = jsonify(response={"success": f"Successfully updated the price to {new_price}."})
    return response, 200


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    key = request.headers.get("api-key")
    if check_key(key):
        chosen_cafe = db.session.execute(db.select(Cafe).filter_by(id=cafe_id)).scalar_one_or_none()
        if chosen_cafe is None:
            response = jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})
            return response, 404
        db.session.delete(chosen_cafe)
        db.session.commit()
        response = jsonify(response={"success": f"Successfully deleted {chosen_cafe.name}."})
        return response
    response = jsonify(error={"Forbidden": "Sorry that's not allowed. Make sure you have the correct api_key."})
    return response, 403


if __name__ == '__main__':
    app.run(debug=True)
