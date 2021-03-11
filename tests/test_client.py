import modbus_client

c = modbus_client.Client(port=5020)
print(c.read_coil(0))
print(c.read_coils(0, 5))
print(c.read_discrete_input(0))
print(c.read_discrete_inputs(0, 5))
print(c.read_discrete_inputs(0, 5))
print(c.read_input_register(0))
print(c.read_input_register(0, encoding="h"))
print(c.read_input_register(0, encoding="e"))
# c.read_coil(1, 1)
