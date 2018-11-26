import logging
import sys

message_broker_host = '0.0.0.0'
message_broker_port_amqp = 5672
message_broker_user = 'admin'
message_broker_password = 'admin'
message_broker_cmd_stop_topic = 'topic://xqa.cmd.stop'
message_broker_db_amqp_insert_event_queue = 'queue://xqa.event'

storage_host = '0.0.0.0'
storage_port = 5432
storage_user = 'xqa'
storage_password = 'xqa'
storage_database_name = 'xqa'
storage_retry_attempts = 5 

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s.%(msecs)03d  %(levelname)8s --- [%(process)5d] %(filename)25s:%(funcName)30s, %(lineno)3s: %(message)s")

logging.getLogger('docker').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
