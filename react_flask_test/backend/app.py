from flask import Flask, request, jsonify
from flask_cors import CORS
from pymodbus.client import ModbusTcpClient
import time

app = Flask(__name__)
CORS(app)  # Allow React to talk to Flask

# --- Modbus Register Addresses ---
PDI_SETVALUE1_ADDR = 5996   # Target Position (32-bit)
PDI_SETVALUE2_ADDR = 5998   # Max Speed (16-bit)
PDI_CMD_ADDR       = 5999   # (low byte)

PDI_STATUS_ADDR    = 4996   # PDI-Status
PDI_RETURN_ADDR    = 4998   # PDI-ReturnValue (Position Feedback) 32-bit
PDI_ERROR_ADDR     = 4997   # Error code

motor_status = "idle"  # Initialize motor status

def move_absolute(target_position, max_speed):
    global motor_status
    motor_status = "moving"
    
    # Set the IP address and port of your Nanotec controller
    ip_address = '10.10.192.90'  # Replace with your Nanotec controller's IP
    port = 502  # Default Modbus TCP port

    # Create a Modbus TCP client
    client = ModbusTcpClient(ip_address, port=port)

    # Connect to the client
    client.connect()

    profile_position_abs(target_position, max_speed, client)

    result = wait_for_target_reached(client)
    if result == "target_reached":
        motor_status = "done"
    elif result.startswith("fault"):
        motor_status = "fault"
    # send NOP command to PDI-Cmd
    client.write_register(5999, 0)
    time.sleep(0.05)  # Short delay just to allow internal processing
    # send switch off command to PDI-Cmd
    client.write_register(5999, 1)

    client.close()
    return result

def profile_position_abs(target_position, max_speed, client: ModbusTcpClient) -> None:
    """ target_position in 0.1 degree, max_speed in rpm """
    # write target position to PDI-SetValue1
    client.write_register(PDI_SETVALUE1_ADDR, target_position >> 16)  # High byte
    client.write_register(PDI_SETVALUE1_ADDR+1, target_position & 0xFFFF)  # Low byte

    # write max speed to PDI-SetValue2
    client.write_register(PDI_SETVALUE2_ADDR, max_speed)

    # send NOP command to PDI-Cmd
    client.write_register(PDI_CMD_ADDR, 0)

    time.sleep(0.05)  # Short delay just to allow internal processing

    # send move command to PDI-Cmd
    client.write_register(PDI_CMD_ADDR, 20)
    print("Move command sent.")

    time.sleep(0.05)  # Short delay just to allow internal processing
    

def wait_for_target_reached(client: ModbusTcpClient) -> None:
    """Wait until the motor reaches the target position."""
    while True:
        status = client.read_input_registers(address=PDI_STATUS_ADDR, count=1).registers[0]
        if status & (1 << 3):  # Bit 3 = PdiStatusTargetReached
            print("Target position reached.")
            return "target_reached"
        elif status & (1 << 2):  # Bit 2 = PdiStatusFault
            print("Fault occurred during move!")
            error = client.read_input_registers(address=PDI_ERROR_ADDR, count=1).registers[0]
            print(f"Error code: {hex(error)}")
            return f"fault: {hex(error)}"
        time.sleep(0.2)

@app.route('/run_function', methods=['POST'])
def run_function():
    data = request.get_json()
    target_position = int(data.get('position', 0))  # Default to 0 if not provided
    max_speed = int(data.get('speed', 0))  # Default to 0 if not provided
    move_absolute(target_position, max_speed)
    return jsonify({'status': 'Function executed successfully'})

@app.route('/motor_status', methods=['GET'])
def get_motor_status():
    return jsonify({'status': motor_status})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
