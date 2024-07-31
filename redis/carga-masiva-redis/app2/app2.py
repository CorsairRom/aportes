import json
import logging
from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

# Configuración de logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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


@app.route('/data/<int:data_id>', methods=['GET'])
def get_data(data_id):
    """
    Obtiene un dato de Redis por ID sino de la DB
    """
    # Obtén todos los elementos de Redis
    result = redis_client.lrange('data', 0, -1)

    dataR = []
    for item in result:
        try:
            item_data = json.loads(item)
            # Verifica que item_data es un diccionario antes de acceder a sus elementos
            if isinstance(item_data, dict) and item_data.get('id') == int(data_id):
                dataR.append(item_data)
        except json.JSONDecodeError as e:
            logger.error('Error decoding JSON: %s', e)

    if dataR:
        return jsonify(dataR[0])
    else :
        dataDB = Data.query.get(data_id)
        if dataDB:
            redis_client.rpush('data', json.dumps({'id': dataDB.id, 'name': dataDB.name}))
            return jsonify({'id': dataDB.id, 'name': dataDB.name})
        else:
            return jsonify({'message': 'Data not found'}), 404


@app.route('/data', methods=['GET'])
def get_all_data():
    result = redis_client.lrange('data', 0, -1)
    if result:
        # Si el dato existe, filtra por ID y devuelve la data correspondiente
        data = [json.loads(item) for item in result]
        logger.info('Data from redis')
        return jsonify(data)
    else:
        data = Data.query.all()
        logger.info('Data from DB')
        for d in data:
            redis_client.rpush('data', json.dumps({'id': d.id, 'name': d.name}))
        return jsonify([{'id': db.id, 'name': db.name} for db in data])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
