import modbus_client
import modbus_server
import pytest
import random
import time
import math  # for math.isclose() to check float equality


@pytest.fixture
def client_server_pair():

    # This isnt completely foolproof, the old port might not be cleaned up:
    port = random.randrange(2000, 60000)

    s = modbus_server.Server(port=port)
    s.start()
    time.sleep(0.1)  # Wait a little for the server socket to exist

    c = modbus_client.Client(port=port)
    yield s, c
    s.stop()


def test_coil(client_server_pair):
    s, c = client_server_pair
    s.set_coil(0, True)
    assert c.read_coil(0) is True


def test_discrete_input(client_server_pair):
    s, c = client_server_pair
    s.set_discrete_input(0, True)
    assert c.read_discrete_input(0) is True


def test_input_register(client_server_pair):
    s, c = client_server_pair
    s.set_input_register(0, 26, encoding="H")
    assert c.read_input_register(0) == 26


def test_input_register_float32(client_server_pair):
    s, c = client_server_pair
    s.set_input_register(0, 1.1, encoding="f")
    assert math.isclose(
        c.read_input_registers(0, number_of_registers=2, encoding="f"),
        1.1,
        rel_tol=10e-5,
    )


def test_input_register_float32_2(client_server_pair):
    s, c = client_server_pair
    for start_address in range(0, 1000, 2):
        random_float32 = random.random() * 10000
        s.set_input_register(0, random_float32, encoding="f")
        assert math.isclose(
            c.read_input_registers(0, number_of_registers=2, encoding="f"),
            random_float32,
            rel_tol=10e-5,
        )


def test_holding_register(client_server_pair):
    s, c = client_server_pair
    s.set_holding_register(0, 25, encoding="H")
    assert c.read_holding_register(0) == 25


def test_holding_register_float32(client_server_pair):
    s, c = client_server_pair
    s.set_holding_register(0, 1.1, encoding="f")
    assert math.isclose(
        c.read_holding_registers(0, number_of_registers=2, encoding="f"),
        1.1,
        rel_tol=10e-5,
    )


def test_holding_register_float32_2(client_server_pair):
    s, c = client_server_pair
    for start_address in range(0, 1000, 2):
        random_float32 = random.random() * 10000
        s.set_holding_register(0, random_float32, encoding="f")
        assert math.isclose(
            c.read_holding_registers(0, number_of_registers=2, encoding="f"),
            random_float32,
            rel_tol=10e-5,
        )
