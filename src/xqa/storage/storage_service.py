import logging

import time

import psycopg2
from psycopg2._json import Json

from xqa.commons import configuration


class StorageService:
    def __init__(self,
                 host=configuration.storage_host,
                 port=configuration.storage_port):
        logging.debug('connecting to: %s@%s:%s' %
                      (configuration.storage_database_name,
                       host,
                       port))
        self._connect(host, port)

    def _connect(self, host, port):
        retry_attempts = configuration.storage_retry_attempts
        connected = False
        while (not connected):
            try:
                self._connection = psycopg2.connect(host=host,
                                                    port=port,
                                                    database=configuration.storage_database_name,
                                                    user=configuration.storage_user,
                                                    password=configuration.storage_password)
                connected = True
            except Exception as exception:
                retry_attempts = retry_attempts - 1
                logging.warning('retry_attempts=%s' % retry_attempts)
                if retry_attempts == 0:
                    raise exception
                time.sleep(2.5)

        self._cursor = self._connection.cursor()

        logging.info('connected to %s:%s' % (host, port))

    def close(self):
        self._cursor.close()
        self._connection.close()

    def insert_event(self, json_string):
        logging.debug('json=%s' % json_string)
        import json
        self._cursor.execute('INSERT INTO events (info) VALUES (%s);' % Json(json.loads(json_string)))
        self._connection.commit()

    def truncate_events(self):
        self._cursor.execute("""TRUNCATE TABLE "events";""")
        self._connection.commit()

    def query_events(self, sql):
        logging.info('sql=%s' % sql)
        self._cursor.execute(sql)
        return self._cursor.fetchall()
