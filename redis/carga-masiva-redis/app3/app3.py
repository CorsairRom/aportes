import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@postgres:5432/mydb'
db = SQLAlchemy(app)

redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

@app.route('/load', methods=['POST'])
def load_data():
    name = request.json.get('name')
    task = {'name': name}
    redis_client.rpush('task_queue', json.dumps(task))
    return jsonify({'status': 'task enqueued'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
