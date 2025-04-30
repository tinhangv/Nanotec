from pymodbus.client import ModbusTcpClient
from tabulate import tabulate
from alibrary.motions.nanotec.state import NanotecDriverState

def read_nanotec(ip_address='10.10.192.90', port=502):
    """Reads Modbus registers from the Nanotec driver and prints the results in a table."""
    # Create and connect the Modbus TCP client
    client = ModbusTcpClient(ip_address, port=port)
    client.connect()

    # Define the registers based on the default mapping, including object addresses
    registers = [
        # Standard Tx PDO 0x3602:xx
        ("Status Word", "0x6041", 5000),
        ("Dummy Object (high byte)", "0x0005", 5001),
        ("Modes-of-Operation Display (low byte)", "0x6061", 5001),
        ("Position Actual Value (part 1)", "0x6064", 5002),
        ("Position Actual Value (part 2)", "0x6064", 5003),
        ("VL Velocity Actual Value", "0x6044", 5004),
        ("Digital Inputs (part 1)", "0x60FD", 5005),
        ("Digital Inputs (part 2)", "0x60FD", 5006),
        # Tx PDO for PDI
        ("PDI Status", "0x2292:01", 4996),
        ("Error Code", "0x603F", 4997),
        ("PDI Return Value (part 1)", "0x2292:02", 4998),
        ("PDI Return Value (part 2)", "0x2292:02", 4999),

        # Standard Rx PDO 0x3502:xx
        ("Control Word", "0x6040", 6000),
        ("Dummy Object (high byte)", "0x0005", 6001),
        ("Modes of Operation (low byte)", "0x6060", 6001),
        ("Target Position (part 1)", "0x607A", 6002),
        ("Target Position (part 2)", "0x607A", 6003),
        ("Profile Velocity (part 1)", "0x6081", 6004),
        ("Profile Velocity (part 2)", "0x6081", 6005),
        ("VL Target Velocity", "0x6042", 6006),
        ("Digital Outputs (part 1)", "0x60FE:01", 6007),
        ("Digital Outputs (part 2)", "0x60FE:01", 6008),
        # Rx PDO for PDI
        ("PDI Set Value 1 (part 1)", "0x2291:01", 5996),
        ("PDI Set Value 1 (part 2)", "0x2291:01", 5997),
        ("PDI Set Value 2", "0x2291:02", 5998),
        ("PDI Set Value 3 (high byte)", "0x2291:03", 5999),
        ("PDI Command (low byte)", "0x2291:04", 5999)
    ]

    def read_register(name, object_address, modbus_address):
        result = client.read_holding_registers(modbus_address)
        if result.isError():
            return [name, object_address, modbus_address, "Error", "Error"]
        value = result.registers[0]
        binary = format(value, '016b')
        return [name, object_address, modbus_address, value, ' '.join(binary[i:i+4] for i in range(0, len(binary), 4))]

    # Prepare data for the table
    data = [read_register(name, obj_addr, modbus_addr) for name, obj_addr, modbus_addr in registers]

    # Print the table
    print(tabulate(data, headers=["Register", "Object", "Modbus", "Value (Dec)", "Value (Bin)"], tablefmt="grid"))

    # Read the status word (register 5000)
    status_word_result = client.read_holding_registers(5000)
    if status_word_result.isError():
        print("Error reading Status Word")
    else:
        status_word = status_word_result.registers[0]
        # Determine the driver's state
        state = NanotecDriverState.from_status_word(status_word)
        print(f"Driver State: {state}")

    # Close the connection
    client.close()

# Ensure the script runs only when executed directly
if __name__ == "__main__":
    read_nanotec()
