import modbus_client
from loguru import logger


def scan(host, port=502):
    c = modbus_client.Client(host=host, port=port, loglevel="CRITICAL")
    print(c.read_coil(0))
    for address in range(65536):
        # print(f"{address} of 65536 ... ")
        print(address, end="\r", flush=True)
        value = c.read_coil(address)
        if value == None:
            # logger.debug(f"Coil {address} not set")
            continue
        # sys.stdout.write("\033[K")
        # sys.stdout.flush()
        logger.info(f"Coil {address} has value {value}")


if __name__ == "__main__":
    host = "localhost"
    port = 2222

    scan(host, port)
