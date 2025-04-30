from pymodbus.client import ModbusTcpClient
import time
from read_nanotec import read_nanotec

def profile_position_abs(target_position,max_speed):
    # write target position to PDI-SetValue1
    client.write_register(5997, target_position & 0xFFFF)  # Low byte
    client.write_register(5996, target_position >> 16)  # High byte

    # write max speed to PDI-SetValue2
    client.write_register(5998, max_speed)

    # send NOP command to PDI-Cmd
    client.write_register(5999, 0)

    time.sleep(0.05)  # Short delay just to allow internal processing

    # send move command to PDI-Cmd
    client.write_register(5999, 20)
    print("Move command sent.")

    time.sleep(0.05)  # Short delay just to allow internal processing

def wait_for_target_reached(client: ModbusTcpClient) -> None:
    """Wait until the motor reaches the target position."""
    while True:
        status = client.read_input_registers(address=4996, count=1).registers[0]
        if status & (1 << 3):  # Bit 3 = PdiStatusTargetReached
            print("Target position reached.")
            break
        elif status & (1 << 2):  # Bit 2 = PdiStatusFault
            print("Fault occurred during move!")
            error = client.read_input_registers(address=4997, count=1).registers[0]
            print(f"Error code: {hex(error)}")
            break
        time.sleep(0.2)

if __name__ == "__main__":
    # Set the IP address and port of your Nanotec controller
    ip_address = '10.10.192.90'  # Replace with your Nanotec controller's IP
    port = 502  # Default Modbus TCP port

    # Create a Modbus TCP client
    client = ModbusTcpClient(ip_address, port=port)

    # Connect to the client
    client.connect()

    max_speed = 25  # Set your desired max speed here
    target_position = 0 # Set your desired target position here
    profile_position_abs(target_position,max_speed)

    wait_for_target_reached(client)
    # send NOP command to PDI-Cmd
    client.write_register(5999, 0)
    time.sleep(0.05)  # Short delay just to allow internal processing
    # send switch off command to PDI-Cmd
    client.write_register(5999, 1)

    client.close()

    # Read and print the Nanotec registers
    read_nanotec()
