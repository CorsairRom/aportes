import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@postgres:5432/mydb'
db = SQLAlchemy(app)

redis_client = redis.StrictRedis(
    host='redis', port=6379, decode_responses=True)


class Data(db.Model):
    """_summary_

    Args:
        db (_type_): _description_
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


@app.route('/load', methods=['POST'])
def load_data():
    """ Load data into the database and Redis """
    name = request.json.get('name')
    data = Data(name=name)
    db.session.add(data)
    db.session.commit()
    # Agrega el ID y nombre del dato a Redis
    redis_client.rpush('data', json.dumps({'id': data.id, 'name': data.name}))
    return jsonify({'id': data.id, 'name': data.name})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
