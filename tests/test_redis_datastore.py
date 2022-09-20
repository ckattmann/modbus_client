import modbus_client
import modbus_server
import pytest
import random
import time
import math  # for math.isclose() to check float equality
import pathlib
import json

import redis


@pytest.fixture
def client_server_pair():

    # This isnt completely foolproof, the old port might not be cleaned up:
    port = random.randrange(2000, 60000)

    s = modbus_server.Server(port=port, datastore=modbus_server.RedisDatastore())
    s.start()
    time.sleep(0.1)  # Wait a little for the server socket to exist

    c = modbus_client.Client(port=port)
    yield s, c
    s.stop()


@pytest.fixture
def client_server_pair_datastore():

    r = redis.Redis(host="localhost", port=6379, db=0)

    with pathlib.Path(__file__).with_name(
        "example_modbus_address_map.json"
    ).open() as f:
        modbus_address_map = json.load(f)
    # Write values into redis:
    for object_reference, addresses in modbus_address_map.items():
        for address, props in addresses.items():
            r.set(f"{props['key']}", props["initial_value"])

    # This isnt completely foolproof, the old port might not be cleaned up:
    port = random.randrange(2000, 60000)
    datastore = modbus_server.RedisDatastore(modbus_address_map=modbus_address_map)
    s = modbus_server.Server(port=port, datastore=datastore)
    s.start()
    time.sleep(0.1)  # Wait a little for the server socket to exist

    c = modbus_client.Client(port=port)
    yield s, c
    s.stop()


# def test_coil(client_server_pair):
#     s, c = client_server_pair
#     s.set_coil(0, True)
#     assert c.read_coil(0) is True


# def test_discrete_input(client_server_pair):
#     s, c = client_server_pair
#     s.set_discrete_input(0, True)
#     assert c.read_discrete_input(0) is True


# def test_input_register(client_server_pair):
#     s, c = client_server_pair
#     s.set_input_register(0, 26, encoding="H")
#     assert c.read_input_register(0) == 26


# def test_holding_register(client_server_pair):
#     s, c = client_server_pair
#     s.set_holding_register(0, 25, encoding="H")
#     assert c.read_holding_register(0) == 25


def test_modbus_address_map(client_server_pair_datastore):
    s, c = client_server_pair_datastore
    # assert c.read_coil(0) == False
    # assert c.read_discrete_input(0) == False
    # assert c.read_discrete_input(1) == True
    # assert c.read_input_register(0) == 25
    # assert c.read_holding_register(0) == 26
    assert math.isclose(c.read_holding_registers(2, 2, "f"), 1.234, rel_tol=10e-5)
