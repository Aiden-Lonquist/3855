import connexion
from connexion import NoContent
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from standard_order import standardOrder
from custom_order import customOrder
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_standard_order(timestamp):
    """ Gets new standard order after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    print(timestamp_datetime)
    readings = session.query(standardOrder).filter(standardOrder.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info(f"Query for standard order after {timestamp} returns {len(results_list)} results")
    logger.info(f"Database running on hostname: {app_config['datastore']['hostname']} and port: {app_config['datastore']['port']}")
    return results_list, 200


def get_custom_order(timestamp):
    """ Gets new custom order after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    print(timestamp_datetime)
    readings = session.query(customOrder).filter(customOrder.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info(f"Query for custom order after {timestamp} returns {len(results_list)} results")
    return results_list, 200


def process_messages():
    """ Process event messages """
    logger.info("starting message process service")
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        if msg["type"] == "standardevent": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()

            so = standardOrder(payload['id'],
                               payload['customer_id'],
                               payload['customer_address'],
                               payload['order_date'])

            session.add(so)

            session.commit()
            session.close()
            logger.debug(f"Stored event standardorder request with a unique id of {payload['id']}")
            logger.info(
                f"Database running on hostname: {app_config['datastore']['hostname']} and port: {app_config['datastore']['port']}")

        elif msg["type"] == "customevent": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()

            co = customOrder(payload['id'],
                             payload['customer_id'],
                             payload['customer_address'],
                             payload['customized_details']['design'],
                             payload['customized_details']['name'],
                             payload['order_date'])

            session.add(co)

            session.commit()
            session.close()
            logger.debug(f"Stored event customorder request with a unique id of {payload['id']}")
            logger.info(
                f"Database running on hostname: {app_config['datastore']['hostname']} and port: {app_config['datastore']['port']}")

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("AidenOrg-Keyboard_Orders-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
