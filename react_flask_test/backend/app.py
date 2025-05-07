from flask import Flask, request, jsonify
from flask_cors import CORS
from pymodbus.client import ModbusTcpClient
from threading import Thread, Lock
import time

app = Flask(__name__)
CORS(app)  # Allow React to talk to Flask

ip_address = '10.10.192.80'  # Replace with your Nanotec controller's IP
port = 502  # Default Modbus TCP port

# --- Modbus Register Addresses ---
PDI_SETVALUE1_ADDR = 5996   # Target Position (32-bit)
PDI_SETVALUE2_ADDR = 5998   # Max Speed (16-bit)
PDI_CMD_ADDR       = 5999   # (low byte)

PDI_STATUS_ADDR    = 4996   # PDI-Status
PDI_RETURN_ADDR    = 4998   # PDI-ReturnValue (Position Feedback) 32-bit
PDI_ERROR_ADDR     = 4997   # Error code

motor_status = "idle"  # Initialize motor status
stop_requested = False
modbus_lock = Lock()

def move(target_position, max_speed, movement_type: str) -> None:
    global motor_status, stop_requested

    motor_status = "moving"
    client = ModbusTcpClient(ip_address, port=port)
    client.connect()

    with modbus_lock:
        if movement_type == "relative":
            profile_position(target_position, max_speed, "relative", client)
        elif movement_type == "absolute":
            profile_position(target_position, max_speed, "absolute", client)
        else:
            print("Invalid movement type. Use 'absolute' or 'relative'.")
            client.close()
            return

    result = wait_for_target_reached(client)

    with modbus_lock:
        # Send NOP before stop or switch-off
        client.write_register(PDI_CMD_ADDR, 0)
        time.sleep(0.05)
        client.write_register(PDI_CMD_ADDR, 1)  # Switch off

    client.close()

    if result == "target_reached":
        motor_status = "done"
    elif result.startswith("fault"):
        motor_status = "fault"
    elif result == "aborted":
        motor_status = "stopped"

def profile_position(target_position, max_speed, movement_type: str, client: ModbusTcpClient) -> None:
    """ target_position in 0.1 degree, max_speed in rpm """
    # write target position to PDI-SetValue1
    target_position &= 0xFFFFFFFF  # Ensure it's a 32-bit value
    client.write_register(PDI_SETVALUE1_ADDR, target_position >> 16)  # High byte
    client.write_register(PDI_SETVALUE1_ADDR+1, target_position & 0xFFFF)  # Low byte

    # write max speed to PDI-SetValue2
    client.write_register(PDI_SETVALUE2_ADDR, max_speed)

    # send NOP command to PDI-Cmd
    client.write_register(PDI_CMD_ADDR, 0)

    time.sleep(0.05)  # Short delay just to allow internal processing

    # send move command to PDI-Cmd
    if movement_type == "absolute":
        client.write_register(PDI_CMD_ADDR, 20)
    elif movement_type == "relative":
        client.write_register(PDI_CMD_ADDR, 21)

    print("Move command sent.")

    time.sleep(0.05)  # Short delay just to allow internal processing
    
def wait_for_target_reached(client: ModbusTcpClient) -> str:
    global stop_requested
    while True:
        if stop_requested:
            print("❗ Movement aborted due to quick stop.")
            stop_requested = False
            return "aborted"

        with modbus_lock:
            status = client.read_input_registers(address=PDI_STATUS_ADDR, count=1).registers[0]

        if status & (1 << 3):
            print("✅ Target position reached.")
            return "target_reached"
        elif status & (1 << 2):
            print("❌ Fault during move!")
            error = client.read_input_registers(address=PDI_ERROR_ADDR, count=1).registers[0]
            print(f"Error code: {hex(error)}")
            return f"fault: {hex(error)}"
        time.sleep(0.2)

@app.route('/quickstop', methods=['POST'])
def quickstop():
    global motor_status, stop_requested
    stop_requested = True

    client = ModbusTcpClient(ip_address, port=port)
    client.connect()

    with modbus_lock:
        client.write_register(PDI_CMD_ADDR, 0)
        time.sleep(0.05)
        client.write_register(PDI_CMD_ADDR, 3)  # Quick stop
    motor_status = "stopped"
    client.close()

    return jsonify({'status': 'Emergency stop sent'})

@app.route('/run_abs_movement', methods=['POST'])
def run_abs_movement():
    data = request.get_json()
    target_position = int(data.get('position', 0))  # Default to 0 if not provided
    max_speed = int(data.get('speed', 0))  # Default to 0 if not provided

    Thread(target=move, args=(target_position, max_speed, "absolute")).start()

    return jsonify({'status': 'Absolute Movement Started'})


@app.route('/run_rel_movement', methods=['POST'])
def run_rel_movement():
    data = request.get_json()
    target_position = int(data.get('position', 0))  # Default to 0 if not provided
    max_speed = int(data.get('speed', 0))  # Default to 0 if not provided

    Thread(target=move, args=(target_position, max_speed, "relative")).start()

    return jsonify({'status': 'Relative Movement Started'})

@app.route('/motor_status', methods=['GET'])
def get_motor_status():
    return jsonify({'status': motor_status})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
