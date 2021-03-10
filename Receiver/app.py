import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient


def process_standard_order(body):
    logger.info(f"Received event standardevent request with a unique id of {body['id']}")
    #requests.post(app_config['standardevent']['url'], json=body)

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "standardevent",
         "datetime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return logger.info(f"Returned event standardevent response(Id: {body['id']}) with status 201"), 201

def process_custom_order(body):
    logger.info(f"Received event customevent request with a unique id of {body['id']}")
    #requests.post(app_config['customevent']['url'], json=body)

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = {"type": "customevent",
         "datetime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return logger.info(f"Returned event customevent response(Id: {body['id']}) with status 201"), 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("AidenOrg-Keyboard_Orders-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    app.run(port=8080)
