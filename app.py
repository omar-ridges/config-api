from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for configurations
configs = {
    "default": {"setting1": "value1", "setting2": "value2"}
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/configs', methods=['GET'])
def list_configs():
    """List all available configuration names"""
    return jsonify({"configs": list(configs.keys())}), 200


@app.route('/config/<name>', methods=['GET'])
def get_config(name):
    """Get a specific configuration by name"""
    if name in configs:
        return jsonify({"name": name, "config": configs[name]}), 200
    return jsonify({"error": "Configuration not found"}), 404


@app.route('/config', methods=['POST'])
def create_config():
    """Create or update a configuration"""
    data = request.get_json()
    if not data or 'name' not in data or 'config' not in data:
        return jsonify({"error": "Missing required fields: name, config"}), 400
    
    name = data['name']
    config = data['config']
    configs[name] = config
    
    return jsonify({"message": "Configuration saved", "name": name}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
