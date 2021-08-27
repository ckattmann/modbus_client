import struct
import socket
import logging

logger = logging.getLogger("modbus_server_logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)-10s: %(message)s")
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)
logger.propagate = False  # prevent double logging


class Client:
    def __init__(self, host="localhost", port=502, unit_id=0):
        self.host = host
        self.port = port
        self.unit_id = unit_id

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.transaction_id = 0

    def send_request(self, function_code, data_frame):

        pdu_frame = struct.pack("!B", function_code) + data_frame

        protocol = 0  # Always 0, reserved for future use (lol)
        length = len(pdu_frame)
        unit_id = self.unit_id
        header_frame = struct.pack(
            "!HHHB",
            self.transaction_id,
            protocol,
            length,
            unit_id,
        )
        adu_frame = header_frame + pdu_frame
        self.s.sendall(adu_frame)
        current_transaction_id = self.transaction_id
        self.transaction_id += 1

        # Send request and get response:
        response = self.s.recv(255)

        ## Extract Header + Function Code:
        # Transaction ID:   (2 Bytes)   Identifies the request-response-pair, is echoed in the response
        # Protocol:         (2 Bytes)   Always 0 ("reserved for future use", lol)
        # Length:           (2 Bytes)   Length of the remaining frame in bytes (Total Length - 6)
        # Unit ID:          (1 Byte)    "Slave ID", inner identifier to route to different units (typically 0)
        # Function Code:    (1 Byte)    1,2,3,4,5,6,15,16,43: Read/Write input/register etc.
        try:
            (
                transaction_id,
                protocol,
                length,
                res_unit_id,
                res_function_code,
            ) = struct.unpack("!HHHBB", response[:8])
            # print(transaction_id, protocol, length, res_unit_id, res_function_code)
        except struct.error:
            logger.error(f"Received incompatible bytes {response}")
            return None

        if transaction_id != current_transaction_id:
            logger.error(f"Received non-matching Transaction ID {transaction_id}")
            return None

        if res_function_code == 128:
            logger.error("Illegal Function")
            return None
        if res_function_code == 129:
            logger.error("Illegal Data Address")
            return None
        if res_function_code == 130:
            logger.error("Illegal Data Value")
            return None
        if res_function_code == 131:
            logger.error("Slave Device Failure")
            return None

        if length != len(response) - 6:
            logger.error(
                f"Response Length field ({length}) not consistent with remaining length of frame ({len(response)-6})"
            )
            return None

        if res_unit_id != self.unit_id:
            logger.error(
                f"Wrong unit ID: Received {res_unit_id}, asked for {self.unit_id}"
            )
            return None

        if res_function_code != function_code:
            logger.error(
                f"Wrong function_code: Received {res_function_code}, requested {function_code}"
            )
            return None

        return response[8:]

    def _read_bits(self, function_code, address, quantity=1):

        if address < 0 or address > 65536:
            raise ValueError(f"Address must be in 0 ... 65536, not {address}")
        if quantity < 1:
            raise ValueError(f"Quantity of registers must be >= 1")
        if function_code in (1, 2) and quantity > 2000:
            raise ValueError(
                f"Quantity of coils/discrete inputs must be < 2000, not {quantity}"
            )

        data_frame = struct.pack("!HH", address, quantity)
        response = self.send_request(function_code, data_frame)
        if not response:  # Error, should be in log
            return None
        data_length = struct.unpack("!B", response[0:1])[0]
        if len(response[1:]) != data_length:
            logger.error(
                f"Wrong data length: Header says {data_length}, data length is {len(response[1:])}"
            )
            return None
        data = response[1:]
        data_ints = struct.unpack(f"!{data_length}B", response[1:])
        bool_list = []
        for data_int in data_ints:
            # There must be a better way! (to convert bytes to a list of booleans)
            bool_list.extend(
                [bool(int(i)) for i in reversed(list(format(data_int, "b")))]
            )

        # Return bool or list(bool):
        if len(bool_list) == 1:
            return bool_list[0]
        else:
            return bool_list

    def _read_registers(self, function_code, address, quantity=1, encoding="H"):
        if not type(address) == int or address < 0 or address > 65535:
            raise ValueError(
                f"Address must be an integer between 0 and 65535, not {address}"
            )
        if quantity < 1:
            raise ValueError(f"Quantity of registers must be >= 1")
        if quantity > 125:
            raise ValueError(f"Quantity of registers must be < 125, not {quantity}")
        if encoding not in ("H", "h", "e", "f"):
            raise ValueError(f"encoding must be 'H', 'h', or 'e'")

        if encoding in ("f"):
            quantity *= 2

        data_frame = struct.pack("!HH", address, quantity)
        response = self.send_request(function_code, data_frame)
        if not response:  # Error, should be in log
            return None
        data_length = struct.unpack("!B", response[0:1])[0]
        if len(response[1:]) != data_length:
            logger.error(
                f"Wrong data length: Header says {data_length}, data length is {len(response[1:])}"
            )
            return None
        number_of_values = data_length // struct.calcsize(encoding)
        values = struct.unpack(f"!{number_of_values}{encoding}", response[1:])

        if len(values) == 1:
            return values[0]
        else:
            return values

    def read_coil(self, address):
        return self._read_bits(1, address)

    def read_coils(self, address, quantity=1):
        return self._read_bits(1, address, quantity)

    def read_discrete_input(self, address, quantity=1):
        return self._read_bits(2, address)

    def read_discrete_inputs(self, address, quantity=1):
        return self._read_bits(2, address, quantity)

    def read_holding_register(self, address, quantity=1, encoding="H"):
        return self._read_registers(3, address, quantity, encoding)

    def read_holding_registers(self, address, encoding="H"):
        return self._read_registers(3, address, encoding=encoding)

    def read_input_register(self, address, quantity=1, encoding="H"):
        return self._read_registers(4, address, quantity, encoding)

    def read_input_registers(self, address, encoding="H"):
        return self._read_registers(4, address, encoding=encoding)
