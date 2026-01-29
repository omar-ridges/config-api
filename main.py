from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# In-memory storage for configurations
configs = {}

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Get all configurations
@app.route('/config', methods=['GET'])
def get_configs():
    return jsonify(configs), 200

# Edge Case: Handle non-existent config name
@app.route('/config/<name>', methods=['GET'])
def get_config(name):
    if name in configs:
        return jsonify({name: configs[name]}), 200
    else:
        return jsonify({"error": "Configuration not found"}), 404

# Edge Case: Handle invalid JSON in request body
# Edge Case: Handle missing name in configuration
@app.route('/config', methods=['POST'])
def create_config():
    try:
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'name' field exists
        if 'name' not in data:
            return jsonify({"error": "Configuration name is required"}), 400
            
        name = data['name']
        
        # Edge Case: Prevent overwriting existing configuration
        if name in configs:
            return jsonify({"error": "Configuration already exists"}), 409
            
        # Edge Case: Validate 'data' field exists
        if 'data' not in data:
            return jsonify({"error": "Configuration data is required"}), 400
            
        configs[name] = data['data']
        return jsonify({"message": "Configuration created successfully"}), 201
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# Edge Case: Handle invalid JSON in request body
# Edge Case: Handle missing name in URL
@app.route('/config/<name>', methods=['PUT'])
def update_config(name):
    try:
        # Edge Case: Validate configuration exists before updating
        if name not in configs:
            return jsonify({"error": "Configuration not found"}), 404
            
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'data' field exists
        if 'data' not in data:
            return jsonify({"error": "Configuration data is required"}), 400
            
        configs[name] = data['data']
        return jsonify({"message": "Configuration updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# Edge Case: Handle missing name in URL
@app.route('/config/<name>', methods=['DELETE'])
def delete_config(name):
    # Edge Case: Validate configuration exists before deleting
    if name in configs:
        del configs[name]
        return jsonify({"message": "Configuration deleted successfully"}), 200
    else:
        return jsonify({"error": "Configuration not found"}), 404

# New endpoint: Partial update of configuration
@app.route('/config/<name>', methods=['PATCH'])
def partial_update_config(name):
    try:
        # Edge Case: Validate configuration exists before updating
        if name not in configs:
            return jsonify({"error": "Configuration not found"}), 404
            
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'data' field exists
        if 'data' not in data:
            return jsonify({"error": "Configuration data is required"}), 400
            
        # Merge existing config with partial update
        if isinstance(configs[name], dict) and isinstance(data['data'], dict):
            configs[name].update(data['data'])
        else:
            configs[name] = data['data']
            
        return jsonify({"message": "Configuration partially updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# New endpoint: Search configurations
@app.route('/config/search', methods=['GET'])
def search_configs():
    try:
        query = request.args.get('query', '')
        key = request.args.get('key', '')
        value = request.args.get('value', '')
        
        results = {}
        
        for config_name, config_data in configs.items():
            match = False
            
            # Search by query string in config name or data
            if query:
                if query.lower() in config_name.lower():
                    match = True
                elif isinstance(config_data, str) and query.lower() in config_data.lower():
                    match = True
                elif isinstance(config_data, dict):
                    config_str = str(config_data).lower()
                    if query.lower() in config_str:
                        match = True
            
            # Search by key-value pair in config data
            elif key and value:
                if isinstance(config_data, dict) and key in config_data:
                    if str(config_data[key]).lower() == value.lower():
                        match = True
            
            # If no search criteria, return all configs
            elif not query and not key and not value:
                match = True
            
            if match:
                results[config_name] = config_data
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": "Search failed"}), 500

# New endpoint: Batch create configurations
@app.route('/config/batch', methods=['POST'])
def batch_create_configs():
    try:
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'configs' field exists
        if 'configs' not in data:
            return jsonify({"error": "Configurations array is required"}), 400
            
        configs_data = data['configs']
        
        # Edge Case: Validate configs is a list
        if not isinstance(configs_data, list):
            return jsonify({"error": "Configurations must be an array"}), 400
            
        created = []
        errors = []
        
        for config_item in configs_data:
            try:
                # Edge Case: Validate 'name' field exists
                if 'name' not in config_item:
                    errors.append({"item": config_item, "error": "Configuration name is required"})
                    continue
                    
                name = config_item['name']
                
                # Edge Case: Prevent overwriting existing configuration
                if name in configs:
                    errors.append({"item": config_item, "error": "Configuration already exists"})
                    continue
                    
                # Edge Case: Validate 'data' field exists
                if 'data' not in config_item:
                    errors.append({"item": config_item, "error": "Configuration data is required"})
                    continue
                    
                configs[name] = config_item['data']
                created.append(name)
            except Exception as e:
                errors.append({"item": config_item, "error": str(e)})
        
        response = {
            "created": created,
            "errors": errors,
            "total_processed": len(configs_data)
        }
        
        status_code = 201 if created and not errors else 207 if created or errors else 400
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# New endpoint: Batch update configurations
@app.route('/config/batch', methods=['PUT'])
def batch_update_configs():
    try:
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'configs' field exists
        if 'configs' not in data:
            return jsonify({"error": "Configurations array is required"}), 400
            
        configs_data = data['configs']
        
        # Edge Case: Validate configs is a list
        if not isinstance(configs_data, list):
            return jsonify({"error": "Configurations must be an array"}), 400
            
        updated = []
        errors = []
        
        for config_item in configs_data:
            try:
                # Edge Case: Validate 'name' field exists
                if 'name' not in config_item:
                    errors.append({"item": config_item, "error": "Configuration name is required"})
                    continue
                    
                name = config_item['name']
                
                # Edge Case: Validate configuration exists before updating
                if name not in configs:
                    errors.append({"item": config_item, "error": "Configuration not found"})
                    continue
                    
                # Edge Case: Validate 'data' field exists
                if 'data' not in config_item:
                    errors.append({"item": config_item, "error": "Configuration data is required"})
                    continue
                    
                configs[name] = config_item['data']
                updated.append(name)
            except Exception as e:
                errors.append({"item": config_item, "error": str(e)})
        
        response = {
            "updated": updated,
            "errors": errors,
            "total_processed": len(configs_data)
        }
        
        status_code = 200 if updated and not errors else 207 if updated or errors else 400
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# New endpoint: Batch delete configurations
@app.route('/config/batch', methods=['DELETE'])
def batch_delete_configs():
    try:
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'names' field exists
        if 'names' not in data:
            return jsonify({"error": "Configuration names array is required"}), 400
            
        names = data['names']
        
        # Edge Case: Validate names is a list
        if not isinstance(names, list):
            return jsonify({"error": "Names must be an array"}), 400
            
        deleted = []
        not_found = []
        
        for name in names:
            if name in configs:
                del configs[name]
                deleted.append(name)
            else:
                not_found.append(name)
        
        response = {
            "deleted": deleted,
            "not_found": not_found,
            "total_processed": len(names)
        }
        
        status_code = 200 if deleted and not not_found else 207 if deleted or not_found else 400
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# New endpoint: Get configuration statistics
@app.route('/config/stats', methods=['GET'])
def get_config_stats():
    try:
        stats = {
            "total_configs": len(configs),
            "config_names": list(configs.keys()),
            "data_types": {},
            "size_estimate": 0
        }
        
        # Analyze data types and estimate size
        for config_name, config_data in configs.items():
            data_type = type(config_data).__name__
            stats["data_types"][data_type] = stats["data_types"].get(data_type, 0) + 1
            
            # Rough size estimate
            stats["size_estimate"] += len(str(config_data))
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": "Failed to get statistics"}), 500

# New endpoint: Validate configuration data
@app.route('/config/validate', methods=['POST'])
def validate_config():
    try:
        data = request.get_json()
        
        # Edge Case: Validate request body is not None
        if data is None:
            return jsonify({"error": "Request body is required"}), 400
            
        # Edge Case: Validate 'data' field exists
        if 'data' not in data:
            return jsonify({"error": "Configuration data is required"}), 400
            
        config_data = data['data']
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "data_type": type(config_data).__name__,
            "size_estimate": len(str(config_data))
        }
        
        # Basic validation checks
        if isinstance(config_data, dict):
            if len(config_data) == 0:
                validation_result["warnings"].append("Empty configuration object")
        elif isinstance(config_data, (list, tuple)):
            if len(config_data) == 0:
                validation_result["warnings"].append("Empty configuration array")
        elif isinstance(config_data, str):
            if len(config_data.strip()) == 0:
                validation_result["errors"].append("Empty configuration string")
                validation_result["valid"] = False
        elif config_data is None:
            validation_result["errors"].append("Configuration data cannot be None")
            validation_result["valid"] = False
        
        # Check for potential circular references in complex objects
        try:
            json.dumps(config_data)
        except (TypeError, ValueError) as e:
            validation_result["errors"].append(f"Configuration data is not JSON serializable: {str(e)}")
            validation_result["valid"] = False
        
        if validation_result["errors"]:
            validation_result["valid"] = False
        
        return jsonify(validation_result), 200
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

# Edge Case: Handle server startup errors
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Failed to start server: {e}")

# Handled Edge Cases: Non-existent config name, invalid JSON in request body, missing name in configuration, missing name in URL, overwriting existing configuration, missing data field, configuration not found for update/delete, server startup errors, missing request body, missing name field
