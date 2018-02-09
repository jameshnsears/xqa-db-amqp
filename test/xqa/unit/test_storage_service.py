import pytest

from xqa.commons import configuration
from xqa.storage.storage_service import StorageService


@pytest.fixture
def dockerpy():
    return [{"image": "jameshnsears/xqa-db:latest",
             "name": "xqa-db",
             'ports': {'%d/tcp' % configuration.storage_port: 5432},
             "network": "xqa"}
            ]


@pytest.mark.timeout(60)
def test_storage_service(dockerpy):
    storage_service = StorageService(port=5432)
    storage_service.truncate_events()

    storage_service.insert_event(
        """{ "service_id": "1", "creation_time": 2, "address": "3", "correlation_id": "4", "subject": "5", "digest": "6" }""")
    storage_service.insert_event(
        """{ "service_id": "11", "creation_time": 22, "address": "33", "correlation_id": "44", "subject": "55", "digest": "66" }""")

    expected_json = [({"correlation_id": "4", "service_id": "1", "creation_time": 2, "subject": "5", "digest": "6",
                       "address": "3"},),
                     ({"correlation_id": "44", "service_id": "11", "creation_time": 22, "subject": "55", "digest": "66",
                       "address": "33"},)
                     ]

    assert storage_service.query_events("""SELECT info FROM "events";""") == expected_json

    storage_service.truncate_events()
    storage_service.close()
