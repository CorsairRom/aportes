from flask import Flask, request, jsonify
import requests
import redis
import json

app = Flask(__name__)

# Configuración de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

DEFAULT_EXPIRATION = 3600

@app.route('/photos', methods=['GET'])
def get_photos():
    album_id = request.args.get('albumId')
    
    try:
        # Intentar obtener los datos de Redis
        photos = redis_client.get('photos')
        if photos:
            print("Data from cache")
            return jsonify(json.loads(photos))
        
        # Si no hay datos en la caché, hacer una solicitud HTTP
        response = requests.get('https://jsonplaceholder.typicode.com/photos', params={'albumId': album_id})
        data = response.json()
        
        # Guardar los datos en Redis
        redis_client.setex('photos', DEFAULT_EXPIRATION, json.dumps(data))
        
        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/photos/<id>', methods=['GET'])
def get_photo(id):
    try:
        response = requests.get(f'https://jsonplaceholder.typicode.com/photos/{id}')
        data = response.json()
        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
