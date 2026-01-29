from flask import Flask, jsonify, request

app = Flask(__name__)

# Initial data store
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

# Helper function to find user by ID
def find_user(user_id):
    return next((user for user in users if user["id"] == user_id), None)

# GET /users - Get all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

# GET /users/<id> - Get user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = find_user(user_id)
    # Edge Case: User not found
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

# POST /users - Create new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Edge Case: Invalid JSON payload
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    # Edge Case: Missing required fields
    if "name" not in data or "email" not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "email": data["email"]
    }
    users.append(new_user)
    return jsonify(new_user), 201

# PUT /users/<id> - Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = find_user(user_id)
    # Edge Case: User not found
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    # Edge Case: Invalid JSON payload
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    # Update user fields if provided
    if "name" in data:
        user["name"] = data["name"]
    if "email" in data:
        user["email"] = data["email"]
    
    return jsonify(user)

# DELETE /users/<id> - Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = find_user(user_id)
    # Edge Case: User not found
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    users.remove(user)
    return jsonify({"message": "User deleted successfully"})

# GET /users/search - Search users by name or email
@app.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '').strip().lower()
    
    # Edge Case: Empty search query
    if not query:
        return jsonify({"error": "Search query parameter 'q' is required"}), 400
    
    # Search users by name or email (case-insensitive)
    filtered_users = [
        user for user in users 
        if query in user["name"].lower() or query in user["email"].lower()
    ]
    
    # Edge Case: No users found matching the query
    if not filtered_users:
        return jsonify({"message": "No users found matching the query", "query": query}), 404
    
    return jsonify({"users": filtered_users, "count": len(filtered_users)})

# New endpoint as requested
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200
# Handled Edge Cases: None (simple health check endpoint)

if __name__ == '__main__':
    app.run(debug=True)
