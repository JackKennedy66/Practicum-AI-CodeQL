from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from marshmallow import Schema, fields, validate, ValidationError
import re

app = Flask(__name__)

users = {}
next_id = 1


class UserSchema(Schema):
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=30),
            validate.Regexp(
                r"^[A-Za-z0-9_]+$",
                error="Username may only contain letters, numbers and underscores"
            )
        ]
    )

    email = fields.Email(required=True)

    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=12, max=128)
    )


user_schema = UserSchema()


def is_strong_password(password):
    return (
        re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": "Invalid input", "details": error.messages}), 400


@app.route("/users", methods=["GET"])
def get_users():
    safe_users = [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        for user in users.values()
    ]

    return jsonify(safe_users), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }), 200


@app.route("/users", methods=["POST"])
def create_user():
    global next_id

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    validated_data = user_schema.load(data)

    if not is_strong_password(validated_data["password"]):
        return jsonify({
            "error": "Password must contain uppercase, lowercase, number and special character"
        }), 400

    for user in users.values():
        if user["username"] == validated_data["username"]:
            return jsonify({"error": "Username already exists"}), 409

        if user["email"] == validated_data["email"]:
            return jsonify({"error": "Email already exists"}), 409

    user = {
        "id": next_id,
        "username": validated_data["username"],
        "email": validated_data["email"],
        "password_hash": generate_password_hash(validated_data["password"])
    }

    users[next_id] = user
    next_id += 1

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    allowed_fields = {"username", "email", "password"}

    if not set(data.keys()).issubset(allowed_fields):
        return jsonify({"error": "Unexpected fields provided"}), 400

    updated_data = user_schema.load(
        {
            "username": data.get("username", user["username"]),
            "email": data.get("email", user["email"]),
            "password": data.get("password", "TempPassword123!")
        }
    )

    if "username" in data:
        user["username"] = updated_data["username"]

    if "email" in data:
        user["email"] = updated_data["email"]

    if "password" in data:
        if not is_strong_password(data["password"]):
            return jsonify({"error": "Weak password"}), 400

        user["password_hash"] = generate_password_hash(data["password"])

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404

    del users[user_id]

    return jsonify({"message": "User deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=False)