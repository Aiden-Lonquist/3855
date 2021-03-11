import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path


def get_stats():
    logger.info("get events method has started")
    if path.exists(app_config['datastore']['filename']):
        with open(app_config["datastore"]["filename"], 'r') as f:
            cur_data = json.load(f)
    else:
        logger.error("attempted to call stats before it was created")
        return "static does not exist", 404
    cur_data.pop('last_updated')
    print(cur_data)
    logger.debug(f"statistics loaded into dictionary: {cur_data}")
    logger.info("request completed")
    return cur_data, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("periodic processing has started")

    '#get the old statistics'
    if path.exists(app_config["datastore"]["filename"]):
        logger.debug("path was found")
        with open(app_config["datastore"]["filename"], 'r') as f:
            cur_data = json.load(f)
    else:
        logger.debug("path was not found")
        cur_data = {"num_standard_order": 0,
                    "max_standard_order_id": 00000000,
                    "num_custom_order": 0,
                    "max_custom_order_id": 00000000,
                    "last_updated": "2001-01-01 01:01:01"
                    }

    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    '#get the standard orders from the database'
    logger.info("getting standard orders")
    try:
        standard_orders = requests.get('http://kafka-3855.eastus2.cloudapp.azure.com:8090/receive/standard?', f'timestamp={cur_data["last_updated"]}')
        if standard_orders.status_code != 200: logger.error(f'standard orders did not get 200')
        logger.info(f"periodic processing received: {len(standard_orders.json())} standard orders")
    except Exception as e:
        logger.debug(f"standard orders error: {e}")
                                       
    '#get the custom orders from the database'
    logger.info("getting custom orders")
    try:
    custom_orders = requests.get('http://kafka-3855.eastus2.cloudapp.azure.com:8090/receive/custom?', f'timestamp={cur_data["last_updated"]}')
    if custom_orders.status_code != 200: logger.error(f'custom orders did not get 200')
    logger.info(f"periodic processing received: {len(custom_orders.json())} custom orders")
    except Exception as e:
        logger.debug(f"custom orders error: {e}")
    
    '#calculate statistics'
    max_standard_order_id = cur_data['max_standard_order_id']
    for i in standard_orders.json():
        if int(i['id']) > max_standard_order_id:
            max_standard_order_id = int(i['id'])
    max_custom_order_id = cur_data['max_custom_order_id']
    for i in custom_orders.json():
        if int(i['id']) > max_custom_order_id:
            max_custom_order_id = int(i['id'])

    num_standard_order = len(standard_orders.json()) + cur_data['num_standard_order']
    num_custom_order = len(custom_orders.json()) + cur_data['num_custom_order']

    '# define the new data'
    logger.info("defining new data")
    new_data = {"num_standard_order": num_standard_order,
                "max_standard_order_id": max_standard_order_id,
                "num_custom_order": num_custom_order,
                "max_custom_order_id": max_custom_order_id,
                "last_updated": cur_date
                }
    with open(app_config["datastore"]["filename"], 'w') as f:
        json.dump(new_data, f, indent=2)
        f.close()
    logger.debug(f"periodic process updated values: {new_data}")
    logger.info("periodic processing has ended")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("AidenOrg-Keyboard_Orders-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
