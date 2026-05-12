import os
import requests
import json
import time
import logging
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

# --- Configuration & Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# Kafka Configuration
conf = {
    'bootstrap.servers': kafka_broker,
    'api.version.request': True
}

TOPIC_NAME = "citibike_status"
STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
INFO_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

# --- Admin Client for Topic Creation/Config ---
def ensure_compacted_topic():
    admin_client = AdminClient(conf)
    topic_config = {
        'cleanup.policy': 'compact',
        'delete.retention.ms': '100',  # Faster cleanup for records marked for deletion
        'segment.ms': '600000'         # Roll segments every 10 mins to trigger compaction sooner
    }
    
    new_topic = NewTopic(
        TOPIC_NAME, 
        num_partitions=1, 
        replication_factor=1, 
        config=topic_config
    )

    fs = admin_client.create_topics([new_topic])
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(f"Topic {topic} created with cleanup.policy=compact")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Topic {topic} already exists. Ensure cleanup.policy is set manually if needed.")
            else:
                logger.error(f"Failed to create topic {topic}: {e}")

try:
    ensure_compacted_topic()
    producer = Producer(conf)
except Exception as e:
    logger.critical(f"Initialization failed: {e}")
    raise

def delivery_report(err, msg):
    """ Callback for message delivery results """
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def fetch_data():
    logger.info("Starting new data ingestion cycle...")
    
    try:
        # Fetch Station Information (Static Data)
        info_resp = requests.get(INFO_URL, timeout=10)
        info_resp.raise_for_status()
        stations_info = {s['station_id']: s for s in info_resp.json()['data']['stations']}
        logger.info(f"Successfully fetched information for {len(stations_info)} stations.")

        # Fetch Station Status (Real-time Data)
        status_resp = requests.get(STATUS_URL, timeout=10)
        status_resp.raise_for_status()
        stations_status = status_resp.json()['data']['stations']
        
        logger.info(f"Processing real-time status for {len(stations_status)} stations.")

        produced_count = 0
        for status in stations_status:
            s_id = status['station_id']
            
            if s_id in stations_info:
                status['lat'] = stations_info[s_id]['lat']
                status['lon'] = stations_info[s_id]['lon']
                status['name'] = stations_info[s_id]['name']
                
                # Stream to Kafka with MESSAGE KEY
                try:
                    producer.produce(
                        TOPIC_NAME, 
                        key=str(s_id),  # REQUIRED FOR COMPACTION
                        value=json.dumps(status).encode('utf-8'),
                        callback=delivery_report
                    )
                    produced_count += 1
                except BufferError:
                    logger.warning("Local producer queue is full, waiting...")
                    producer.poll(0.1)

        producer.flush()
        logger.info(f"Successfully streamed {produced_count} enriched records to topic: {TOPIC_NAME}")

    except requests.exceptions.RequestException as re:
        logger.error(f"Network error while fetching data: {re}")
    except Exception as e:
        logger.exception(f"Unexpected error during data processing: {e}")

if __name__ == "__main__":
    logger.info("CitiBike Data Producer service started.")
    try:
        while True:
            fetch_data()
            logger.info("Cycle complete. Sleeping for 60 seconds...")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Service interrupted by user. Shutting down...")
    finally:
        producer.flush()