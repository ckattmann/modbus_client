# modbus_client
An easy-to-use ModbusTCP Client in pure Python.

## Installation
```shell
pip install modbus_client
```
modbus_client requires no external packages apart from the Python Standard Library. It works with Python 3.6+.

## Example Usage
```python
import modbus_client

c = modbus_client.Client(host='localhost', port=502)

c.read_coil(0)  # return True or False or throws an error
c.read_coils(0, number_of_bits=2)

c.read_discrete_input(0)
c.read_discrete_inputs(0, number_of_bits=2)

c.read_holding_register(0)
c.read_holding_registers(0, number_of_registers=2, encoding='h')

c.read_input_register(0)
c.read_input_registers(0, number_of_registers=2, encoding='f')
```

## Functions
### Client Object
`c = modbus_client.Client(host='127.0.0.1', port=502, unit_id=0)`

Instantiate a connection object which can execute various read functions on the Modbus connection. The default `port` for Modbus, 502, requires root to access. `unit_id` is a Modbus-internal parameters which can discern between different sub-devices which is irrelevant if you are directly connected to a device.


### Read Coils and Discrete Inputs
`c.read_coil(address)`

`c.read_discrete_input(address)`

Read one coil register and return the result as a boolean.

`c.read_coils(start_address, number_of_bits=1)`

`c.read_discrete_inputs(start_address, number_of_bits=1)`

Read multiple coils and return the result in a list of booleans.


### Holding and Input Registers
`c.read_holding_register(address, encoding='H')`

`c.read_input_register(address, encoding='H')`

Read one holding or input register and return the result decoded with the given encoding (see below). To read a 32 or 64 bit value, use the functions for multiple registers below.

`c.read_holding_registers(0, number_of_registers=2, encoding='H')`

`c.read_input_registers(0, number_of_registers=2, encoding='H')`

Read multiple holding or input registers and return the decoded result. To read one 32 bit value, use `number_of_registers=2`.

## Encodings
| encoding | Data Type | Bytes | Registers |
|----------|-----------|------:|----------:|
|`h` | signed short | 2| 1|
|`H` | unsigned short | 2| 1|
|`e` | float16 | 2| 1|
|`f` | float32 | 4| 2|
