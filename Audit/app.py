import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin


def get_standard_order(index):
    """ Get standard order in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving standard order at index %d" % index)
    try:
        msg_num = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg_num == index and msg['type'] == 'standardevent':
                logger.info(f"found and returned message with ID: {msg['payload']['id']} at index: {index}")
                return msg, 200
            elif msg['type'] == 'standardevent':
                msg_num += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find standard order at index %d" % index)
    return {"message": "Not Found"}, 404


def get_custom_order(index):
    """ Get custom order in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving custom order at index %d" % index)
    try:
        msg_num = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg_num == index and msg['type'] == 'customevent':
                logger.info(f"found and returned message with ID: {msg['payload']['id']} at index: {index}")
                return msg, 200
            elif msg['type'] == 'customevent':
                msg_num += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find custom order at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("AidenOrg-Keyboard_Orders-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    app.run(port=8110)
