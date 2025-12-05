import json
import urllib.parse
import os

def convert_thunder_to_postman(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            thunder_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{input_file}'.")
        return

    postman_collection = {
        "info": {
            "name": "Thunder Client Export",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Thunder Client export might be a list of requests or a collection object
    # Based on the user's file view, it looks like a list of request objects directly.
    requests_list = thunder_data if isinstance(thunder_data, list) else thunder_data.get('requests', [])

    for req in requests_list:
        # Basic fields
        name = req.get('name', 'Untitled Request')
        method = req.get('method', 'GET')
        url_raw = req.get('url', '')
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url_raw)
        
        # Construct Postman URL object
        pm_url = {
            "raw": url_raw,
            "protocol": parsed_url.scheme,
            "host": parsed_url.netloc.split('.'),
            "path": parsed_url.path.strip('/').split('/'),
            "query": []
        }
        
        # Handle Query Params
        # Thunder Client stores them in 'params' list or embedded in URL
        # We will prefer the 'params' list if it exists and merge/handle duplicates if needed
        # For simplicity, we'll map the Thunder Client 'params' to Postman 'query'
        tc_params = req.get('params', [])
        for param in tc_params:
            pm_url['query'].append({
                "key": param.get('name', ''),
                "value": param.get('value', ''),
                "disabled": param.get('isDisabled', False)
            })

        # If params are empty but URL has query string, parse it?
        # Postman import usually handles 'raw' URL well, but explicit query params are better.
        # If Thunder Client 'params' is empty, we rely on the raw URL.
        
        # Headers
        pm_headers = []
        tc_headers = req.get('headers', [])
        for header in tc_headers:
            pm_headers.append({
                "key": header.get('name', ''),
                "value": header.get('value', ''),
                "disabled": header.get('isDisabled', False)
            })

        # Body (if applicable)
        pm_body = {}
        body_raw = req.get('body', {}).get('raw', '')
        if body_raw:
             pm_body = {
                "mode": "raw",
                "raw": body_raw
            }
        # Note: Thunder Client might have other body types (form-data, etc.), 
        # but the provided snippet showed mostly GETs. 
        # We can add more robust body handling if needed.

        postman_request = {
            "name": name,
            "request": {
                "method": method,
                "header": pm_headers,
                "url": pm_url
            }
        }
        
        if pm_body:
            postman_request['request']['body'] = pm_body

        postman_collection['item'].append(postman_request)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(postman_collection, f, indent=4)
        print(f"Successfully converted {len(postman_collection['item'])} requests to '{output_file}'.")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    # Define paths based on user's workspace
    # Using the path from the user's open file
    input_path = r"c:\Users\Robert Yang\Documents\_project_\GitHub\bobyang3\tvbox\TVBoxOSC\~\thunderActivity.json"
    output_path = r"c:\Users\Robert Yang\Documents\_project_\GitHub\bobyang3\tvbox\TVBoxOSC\~\echoapi_import.json"
    
    # Ensure the directory exists (it should, as the input file is there)
    # The path has a '~' which might be a valid directory name or a representation of something else.
    # I will use the exact string provided in the context.
    
    convert_thunder_to_postman(input_path, output_path)
