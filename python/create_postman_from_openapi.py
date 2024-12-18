import json
import sys

def create_postman_collection_from_openapi(openapi_file_path, collection_name):
    try:
        # Load and parse OpenAPI file
        with open(openapi_file_path, "r") as file:
            openapi_data = json.load(file)

        # Initialize Postman Collection structure
        postman_collection = {
            "info": {
                "name": collection_name,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [],
        }

        # Add variables (global variables from OpenAPI servers and components)
        if "servers" in openapi_data:
            for idx, server in enumerate(openapi_data["servers"]):
                variable_name = f"server{idx + 1}_url"
                postman_collection["variable"].append({
                    "key": variable_name,
                    "value": server["url"]
                })

        # Parse paths and create requests
        if "paths" in openapi_data:
            for path, path_item in openapi_data["paths"].items():
                for method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    if method in path_item:
                        operation = path_item[method]
                        request_item = {
                            "name": operation.get("operationId", f"{method.upper()} {path}"),
                            "request": {
                                "method": method.upper(),
                                "header": [],
                                "url": {
                                    "raw": f"{{{{server1_url}}}}{path}",
                                    "host": ["{{server1_url}}"],
                                    "path": path.strip("/").split("/")
                                },
                            }
                        }

                        # Add parameters
                        if "parameters" in operation:
                            request_item["request"]["url"]["query"] = []
                            for param in operation["parameters"]:
                                request_item["request"]["url"]["query"].append({
                                    "key": param["name"],
                                    "value": param.get("example", ""),
                                    "description": param.get("description", ""),
                                    "disabled": not param.get("required", False)
                                })

                        # Add requestBody if present
                        if "requestBody" in operation and "content" in operation["requestBody"]:
                            for content_type, media_type in operation["requestBody"]["content"].items():
                                if "example" in media_type:
                                    body = media_type["example"]
                                elif "schema" in media_type and "example" in media_type["schema"]:
                                    body = media_type["schema"]["example"]
                                else:
                                    body = {}

                                request_item["request"]["body"] = {
                                    "mode": "raw",
                                    "raw": json.dumps(body, indent=2),
                                    "options": {
                                        "raw": {
                                            "language": "json"
                                        }
                                    }
                                }
                                request_item["request"]["header"].append({
                                    "key": "Content-Type",
                                    "value": content_type
                                })

                        # Add to Postman Collection
                        postman_collection["item"].append(request_item)

        # Handle Authentication (global or per-operation)
        if "components" in openapi_data and "securitySchemes" in openapi_data["components"]:
            for scheme_name, scheme in openapi_data["components"]["securitySchemes"].items():
                if scheme["type"] == "http" and scheme["scheme"] == "bearer":
                    postman_collection["variable"].append({
                        "key": "auth_bearer_token",
                        "value": "",
                        "type": "string"
                    })
                    for item in postman_collection["item"]:
                        item["request"]["header"].append({
                            "key": "Authorization",
                            "value": "Bearer {{auth_bearer_token}}"
                        })

        # Output Postman Collection JSON
        output_file = f"{collection_name.replace(' ', '_').lower()}_postman_collection.json"
        with open(output_file, "w") as file:
            json.dump(postman_collection, file, indent=2)

        print(f"Postman Collection created: {output_file}")

    except FileNotFoundError:
        print("OpenAPI file not found.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <openapi_file_path> <collection_name>")
    else:
        openapi_file_path = sys.argv[1]
        collection_name = sys.argv[2]
        create_postman_collection_from_openapi(openapi_file_path, collection_name)
