import base64
from unittest.mock import ANY

import pytest

from rhub.satellite import model


API_BASE = '/v0'


def _db_add_row_side_effect(data_added):
    def side_effect(row):
        for k, v in data_added.items():
            setattr(row, k, v)
    return side_effect


def test_list_servers(client, keycloak_mock):
    model.SatelliteServer.query.limit.return_value.offset.return_value = [
        model.SatelliteServer(
            id=1,
            name='test',
            description='',
            owner_group_id='00000000-0000-0000-0000-000000000000',
            hostname='satellite.example.com',
            insecure=False,
            credentials='kv/test',
        ),
    ]
    model.SatelliteServer.query.count.return_value = 1

    keycloak_mock.group_get_name.return_value = 'test-group'

    rv = client.get(
        f'{API_BASE}/satellite/server',
        headers={'Authorization': 'Bearer foobar'},
    )

    assert rv.status_code == 200, rv.data
    assert rv.json == {
        'data': [
            {
                'id': 1,
                'name': 'test',
                'description': '',
                'owner_group_id': '00000000-0000-0000-0000-000000000000',
                'owner_group_name': 'test-group',
                'hostname': 'satellite.example.com',
                'insecure': False,
                'credentials': 'kv/test',
                '_href': ANY,
            }
        ],
        'total': 1,
    }


def test_get_server(client, keycloak_mock):
    model.SatelliteServer.query.get.return_value = model.SatelliteServer(
        id=1,
        name='test',
        description='',
        owner_group_id='00000000-0000-0000-0000-000000000000',
        hostname='satellite.example.com',
        insecure=False,
        credentials='kv/test',
    )

    keycloak_mock.group_get_name.return_value = 'test-group'

    rv = client.get(
        f'{API_BASE}/satellite/server/1',
        headers={'Authorization': 'Bearer foobar'},
    )

    model.SatelliteServer.query.get.assert_called_with(1)

    assert rv.status_code == 200, rv.data
    assert rv.json == {
        'id': 1,
        'name': 'test',
        'description': '',
        'owner_group_id': '00000000-0000-0000-0000-000000000000',
        'owner_group_name': 'test-group',
        'hostname': 'satellite.example.com',
        'insecure': False,
        'credentials': 'kv/test',
        '_href': ANY,
    }


def test_create_server(client, db_session_mock, keycloak_mock, mocker):
    server_data = {
        'name': 'test',
        'owner_group_id': '00000000-0000-0000-0000-000000000000',
        'hostname': 'satellite.example.com',
        'insecure': True,
        'credentials': 'kv/test',
    }

    model.SatelliteServer.query.filter.return_value.count.return_value = 0
    db_session_mock.add.side_effect = _db_add_row_side_effect({'id': 1})

    keycloak_mock.group_get_name.return_value = 'test-group'

    rv = client.post(
        f'{API_BASE}/satellite/server',
        headers={'Authorization': 'Bearer foobar'},
        json=server_data,
    )

    assert rv.status_code == 200, rv.data

    db_session_mock.add.assert_called()

    server = db_session_mock.add.call_args.args[0]
    for k, v in server_data.items():
        assert getattr(server, k) == v


def test_update_server(client, keycloak_mock):
    server = model.SatelliteServer(
        id=1,
        name='test',
        description='',
        owner_group_id='00000000-0000-0000-0000-000000000000',
        hostname='satellite.example.com',
        insecure=False,
        credentials='kv/test',
    )
    model.SatelliteServer.query.get.return_value = server

    keycloak_mock.group_get_name.return_value = 'test-group'

    rv = client.patch(
        f'{API_BASE}/satellite/server/1',
        headers={'Authorization': 'Bearer foobar'},
        json={
            'name': 'new',
            'description': 'new desc',
        },
    )

    assert rv.status_code == 200, rv.data

    model.SatelliteServer.query.get.assert_called_with(1)

    assert server.name == 'new'
    assert server.description == 'new desc'


def test_delete_server(client, db_session_mock, keycloak_mock):
    server = model.SatelliteServer(
        id=1,
        name='test',
        description='',
        owner_group_id='00000000-0000-0000-0000-000000000000',
        hostname='satellite.example.com',
        insecure=False,
        credentials='kv/test',
    )
    model.SatelliteServer.query.get.return_value = server

    keycloak_mock.group_get_name.return_value = 'test-group'

    rv = client.delete(
        f'{API_BASE}/satellite/server/1',
        headers={'Authorization': 'Bearer foobar'},
    )

    assert rv.status_code == 204, rv.data

    model.SatelliteServer.query.get.assert_called_with(1)
    db_session_mock.delete.assert_called_with(server)
