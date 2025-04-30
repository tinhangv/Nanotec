from pymodbus.client import ModbusTcpClient
import struct
import time

# --- Modbus Register Addresses ---
PDI_SETVALUE1_ADDR = 5996   # Target Position (32-bit)
PDI_SETVALUE2_ADDR = 5998   # Max Speed (16-bit)
PDI_CMD_ADDR       = 5999   # (low byte)

PDI_STATUS_ADDR    = 4996   # PDI-Status
PDI_RETURN_ADDR    = 4998   # PDI-ReturnValue (Position Feedback) 32-bit
PDI_ERROR_ADDR     = 4997   # Error code

def clear_fault(client: ModbusTcpClient) -> None:
    """Clear any fault present in the motor."""
    status = client.read_input_registers(address=PDI_STATUS_ADDR, count=1).registers[0]
    if status & (1 << 2):  # Check if fault bit is set
        print("Fault detected. Clearing...")
        clear_cmd = (0 & 0xFF) | (2 << 8)  # Clear Error = 2
        client.write_register(PDI_CMD_ADDR, clear_cmd)
        time.sleep(0.5)

def set_target_position(client: ModbusTcpClient, target_position: int) -> None:
    """Set the target position for the motor."""
    pos_bytes = struct.pack('<i', target_position)
    pos_regs = struct.unpack('<HH', pos_bytes)
    client.write_registers(PDI_SETVALUE1_ADDR, pos_regs)

def set_max_speed(client: ModbusTcpClient, max_speed: int) -> None:
    """Set the maximum speed for the motor."""
    client.write_register(PDI_SETVALUE2_ADDR, max_speed & 0xFFFF)

def send_nop_command(client: ModbusTcpClient) -> None:
    """Send a NOP (No Operation) command to the motor."""
    current_value = client.read_holding_registers(5999, count=1).registers[0]
    high_byte = current_value & 0xFF00  # Extract the high byte
    nop_cmd = high_byte | (0 & 0xFF)  # Combine with NOP command
    client.write_register(5999, nop_cmd)
    time.sleep(0.1)

def send_move_command(client: ModbusTcpClient) -> None:
    """Send a move command to the motor."""
    current_value = client.read_holding_registers(5999, count=1).registers[0]
    high_byte = current_value & 0xFF00  # Extract the high byte
    move_cmd = high_byte | (20 & 0xFF)  # Combine with move command
    client.write_register(5999, move_cmd)

def wait_for_target_reached(client: ModbusTcpClient) -> None:
    """Wait until the motor reaches the target position."""
    while True:
        status = client.read_input_registers(address=PDI_STATUS_ADDR, count=1).registers[0]
        if status & (1 << 3):  # Bit 3 = PdiStatusTargetReached
            print("Target position reached.")
            break
        elif status & (1 << 2):  # Bit 2 = PdiStatusFault
            print("Fault occurred during move!")
            error = client.read_input_registers(address=PDI_ERROR_ADDR, count=1).registers[0]
            print(f"Error code: {hex(error)}")
            break
        time.sleep(0.2)

def get_actual_position(client: ModbusTcpClient) -> int:
    """Get the actual position of the motor."""
    ret_vals = client.read_input_registers(address=PDI_RETURN_ADDR, count=2).registers
    ret_bytes = struct.pack('<HH', *ret_vals)
    actual_position = struct.unpack('<i', ret_bytes)[0]
    return actual_position

# Example usage in a main program
if __name__ == "__main__":
    ip_address = '10.10.192.90'  # Replace with your Nanotec controller's IP
    port = 502  # Default Modbus TCP port

    # Connect to the motor
    client = ModbusTcpClient(ip_address, port=port)

    try:
        # Clear any fault
        clear_fault(client)

        # Set motion parameters
        target_position = 5000  # Example target position
        max_speed = 20  # Example max speed
        set_target_position(client, target_position)
        set_max_speed(client, max_speed)

        # Send commands
        send_nop_command(client)
        send_move_command(client)

        # Wait for the motor to reach the target
        wait_for_target_reached(client)

        # Get and print the actual position
        actual_position = get_actual_position(client)
        print(f"Final position: {actual_position}")

    finally:
        # Close the connection
        client.close()
