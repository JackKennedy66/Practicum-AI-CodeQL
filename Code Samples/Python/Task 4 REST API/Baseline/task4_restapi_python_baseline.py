from flask import Flask, request, jsonify

app = Flask(__name__)

users = {}
next_id = 1


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(list(users.values())), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@app.route("/users", methods=["POST"])
def create_user():
    global next_id

    data = request.get_json()

    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "Username and email are required"}), 400

    user = {
        "id": next_id,
        "username": data["username"],
        "email": data["email"]
    }

    users[next_id] = user
    next_id += 1

    return jsonify(user), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if "username" in data:
        user["username"] = data["username"]

    if "email" in data:
        user["email"] = data["email"]

    return jsonify(user), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404

    del users[user_id]

    return jsonify({"message": "User deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)