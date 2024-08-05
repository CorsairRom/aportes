import json
import logging
from flask import Flask, jsonify
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
    name = db.Column(db.String(150))

@app.route('/data', methods=['GET'])
def get_all_data():
    """Get all data from the database."""
    data = Data.query.order_by(Data.id).all()
    logger.info('Data from DB')
    #data.sort()
    logger.info(data)
    return jsonify([{'id': db.id, 'name': db.name} for db in data])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
