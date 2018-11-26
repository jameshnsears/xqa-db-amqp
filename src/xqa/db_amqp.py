import argparse
import logging
from uuid import uuid4

from proton.handlers import MessagingHandler
from proton.reactor import Container

from xqa.commons import configuration
from xqa.commons.xqa_messaging_handler import XqaMessagingHandler
from xqa.storage.storage_service import StorageService


class DbAmqp(XqaMessagingHandler):
    def __init__(self,
                 message_broker_host=configuration.message_broker_host,
                 storage_host=configuration.storage_host,
                 storage_port=configuration.storage_port):
        XqaMessagingHandler.__init__(self)
        MessagingHandler.__init__(self)

        self._message_broker_host = message_broker_host
        self._stopping = False
        self._service_id = str(uuid4()).split('-')[0]

        logging.info('%s/%s' % (self.__class__.__name__.lower(), self._service_id))
        logging.debug('-message_broker_host=%s' % message_broker_host)
        logging.debug('-storage_host=%s' % storage_host)
        logging.debug('-storage_port=%s' % storage_port)

        self._storage_service = StorageService(host=storage_host,
                                               port=storage_port)

    def on_start(self, event):
        message_broker_url = 'amqp://%s:%s@%s:%s/' % (configuration.message_broker_user,
                                                      configuration.message_broker_password,
                                                      self._message_broker_host,
                                                      configuration.message_broker_port_amqp)

        connection = event.container.connect(message_broker_url, reconnect=XqaMessagingHandler.XqaBackoff())
        self.container = event.reactor

        self.queue_db_amqp_insert = event.container.create_receiver(connection,
                                                                    configuration.message_broker_db_amqp_insert_event_queue)

        self.cmd_stop_receiver = event.container.create_receiver(connection,
                                                                 configuration.message_broker_cmd_stop_topic)

        logging.info('connected to %s:%d' % (configuration.message_broker_host, configuration.message_broker_port_amqp))

    def on_message(self, event):
        if configuration.message_broker_db_amqp_insert_event_queue in event.message.address:
            self._insert_event_into_storage(event)
            return

        if configuration.message_broker_cmd_stop_topic in event.message.address:
            self._cmd_stop(event)
            return

    def _insert_event_into_storage(self, event):
        logging.info('%s creation_time=%s; correlation_id=%s; address=%s; subject=%s; body=%s',
                     '>',
                     event.message.creation_time,
                     event.message.correlation_id,
                     event.message.address,
                     event.message.subject,
                     event.message.body.decode('utf-8'))

        self._storage_service.insert_event(event.message.body.decode('utf-8'))

    def _cmd_stop(self, event):
        logging.info('%s creation_time=%s; correlation_id=%s; address=%s; subject=%s; digest(body)=%s',
                     '>',
                     event.message.creation_time,
                     event.message.correlation_id,
                     event.message.address,
                     event.message.subject,
                     event.message.body)

        self._storage_service.close()
        super()._cmd_stop(event)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-message_broker_host', '--message_broker_host', required=True,
                            help='i.e. xqa-message-broker')
        parser.add_argument('-storage_host', '--storage_host', required=True,
                            help='i.e. xqa-db')
        parser.add_argument('-storage_port', '--storage_port', required=True,
                            help='i.e. 5432')
        args = parser.parse_args()

        Container(DbAmqp(message_broker_host=args.message_broker_host,
                         storage_host=args.storage_host,
                         storage_port=args.storage_port)).run()
    except Exception as exception:
        logging.error(exception)
        exit(-1)
