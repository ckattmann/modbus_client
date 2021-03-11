# modbus_client
An easy-to-use ModbusTCP Client in pure Python.

## Installation
```shell
pip install modbus_client
```
modbus_client requires no external packages apart from the Python Standard Library. It works with Python 3.6+.

## Usage
```python
import modbus_client

c = modbus_client.Client(host='localhost', port=502)

c.read_coil(0)  # return True or False or throws an error
```
