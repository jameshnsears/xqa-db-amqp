import ast
import logging
import os
import subprocess
from uuid import uuid4

import pytest
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from xqa.commons import configuration
from xqa.commons.xqa_messaging_handler import XqaMessagingHandler
from xqa.storage.storage_service import StorageService


class DbAmqpTest(XqaMessagingHandler):
    def __init__(self):
        XqaMessagingHandler.__init__(self)
        MessagingHandler.__init__(self)
        logging.info(self.__class__.__name__)
        self._stopping = False

        self._insert_event_sent = False
        self._event_placed_in_storage = False

        self._empty_storage()

        self._json = """{ "service_id": "1", "creation_time": 2, "address": "3", "correlation_id": "4", "subject": "©", "digest": "6" }"""

    def _empty_storage(self):
        self._storage_service = StorageService(port=5432)
        self._storage_service.truncate_events()

    def on_start(self, event):
        message_broker_url = 'amqp://%s:%s@%s:%s/' % (configuration.message_broker_user,
                                                      configuration.message_broker_password,
                                                      configuration.message_broker_host,
                                                      configuration.message_broker_port_amqp)
        connection = event.container.connect(message_broker_url)
        self.container = event.reactor

        self.insert_event_sender = event.container.create_sender(connection,
                                                                 configuration.message_broker_db_amqp_insert_event_queue)

        self.cmd_stop_sender = event.container.create_sender(connection, configuration.message_broker_cmd_stop_topic)
        self.cmd_stop_receiver = event.container.create_receiver(connection,
                                                                 configuration.message_broker_cmd_stop_topic)

        self.container.schedule(1, self)

    def on_timer_task(self, event):
        if not self._insert_event_sent:
            self._send_insert_event()

        elif not self._event_placed_in_storage:
            self._check_storage_received_insert()

        elif self._insert_event_sent and self._event_placed_in_storage:
            self._send_cmd_stop()

        self.container.schedule(1, self)

    def _send_insert_event(self):
        message = Message(address=configuration.message_broker_db_amqp_insert_event_queue,
                          correlation_id=str(uuid4()),
                          creation_time=XqaMessagingHandler.now_timestamp_seconds(),
                          body=self._json.encode('utf-8'))

        self.insert_event_sender.send(message)

        logging.info('%s creation_time=%s; correlation_id=%s; address=%s; reply_to=%s; expiry_time=%s; body=%s',
                     '<',
                     message.creation_time,
                     message.correlation_id,
                     message.address,
                     message.reply_to,
                     message.expiry_time,
                     message.body)

        self._insert_event_sent = True

    def _check_storage_received_insert(self):
        storage_event = self._storage_service.query_events('''SELECT info FROM "events";''')
        if storage_event:
            assert storage_event[0][0] == ast.literal_eval(self._json)
            self._storage_service.close()
            self._event_placed_in_storage = True

    def on_message(self, event):
        logging.info('%s creation_time=%s; correlation_id=%s; address=%s; reply_to=%s; expiry_time=%s, body=%s',
                     '>',
                     event.message.creation_time,
                     event.message.correlation_id,
                     event.message.address,
                     event.message.reply_to,
                     event.message.expiry_time,
                     event.message.body)

        if configuration.message_broker_cmd_stop_topic in event.message.address:
            self._cmd_stop(event)

    def _send_cmd_stop(self):
        message = Message(address=configuration.message_broker_cmd_stop_topic,
                          correlation_id=str(uuid4()),
                          creation_time=XqaMessagingHandler.now_timestamp_seconds())

        logging.info('%s creation_time=%s; correlation_id=%s; address=%s; reply_to=%s; expiry_time=%s',
                     '<',
                     message.creation_time,
                     message.correlation_id,
                     message.address,
                     message.reply_to,
                     message.expiry_time)

        self.cmd_stop_sender.send(message)


@pytest.fixture
def dockerpy():
    return [{'image': 'jameshnsears/xqa-db:latest',
             'name': 'xqa-db',
             'ports': {'%d/tcp' % configuration.storage_port: 5432},
             'network': 'xqa'},
            {'image': 'jameshnsears/xqa-message-broker:latest',
             'name': 'xqa-message-broker',
             'ports': {'%d/tcp' % configuration.message_broker_port_amqp: configuration.message_broker_port_amqp,
                       '8161/tcp': 8161},
             'network': 'xqa'},
            ]


# @pytest.mark.timeout(120)
def test_db_amqp(dockerpy):
    subprocess.Popen([
        'python3',
        os.path.join(os.path.dirname(__file__), '../../../src/xqa/db_amqp.py'),
        '-message_broker_host', '0.0.0.0',
        '-storage_host', '0.0.0.0',
        '-storage_port', '5432'])

    try:
        Container(DbAmqpTest()).run()
    except Exception as exception:
        logging.error(exception)
