from pymodbus.client import ModbusTcpClient
from tabulate import tabulate
from alibrary.motions.nanotec.state import NanotecDriverState

def read_nanotec(ip_address='10.10.192.100', port=502):
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
        ("Position Actual Value", "0x6064", 5002),
        ("Position Actual Value", "0x6064", 5003),
        ("VL Velocity Actual Value", "0x6044", 5004),
        ("Digital Inputs", "0x60FD", 5005),
        ("Digital Inputs", "0x60FD", 5006),
        # Standard Rx PDO 0x3502:xx 
        ("Control Word", "0x6040", 6000),
        ("Dummy Object (high byte)", "0x0005", 6001),
        ("Modes of Operation (low byte)", "0x6060", 6001),
        ("Target Position", "0x607A", 6004),
        ("Target Position", "0x607A", 6005),
        ("Profile Velocity", "0x6081", 6006),
        ("Profile Velocity", "0x6081", 6007),
        ("VL Target Velocity", "0x6042", 6008),
        ("Digital Outputs", "0x60FE:01", 6009),
        ("Digital Outputs", "0x60FE:01", 6010)
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
