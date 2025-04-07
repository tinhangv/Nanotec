from pymodbus.client import ModbusTcpClient
import time
from read_nanotec import read_nanotec

# Set the IP address and port of your Nanotec controller
ip_address = '10.10.192.100'  # Replace with your Nanotec controller's IP
port = 502  # Default Modbus TCP port

# Create a Modbus TCP client
client = ModbusTcpClient(ip_address, port=port)

# Connect to the client
client.connect()

# MODES OF OPERATION
# client.write_register(6001, 1) # Profile Position
# client.write_register(6001, 3) # Profile Velocity

# CHANGING STATES
# client.write_register(6000, 0x6)  # "ready to switch on"
# client.write_register(6000, 0x7)  # "switched on"
# client.write_register(6000, 0xF)  # "operation enabled"

# MOVEMENT PARAMETERS
# # set profile velocity 
# client.write_register(6006, 0)
# client.write_register(6007, 50)

# # set target velocity 
# client.write_register(6008, 50)

# #set target position 
# client.write_register(6004, 0x0)
# client.write_register(6005, 2000)

# # start relative positioning motion (bit 6 on)
# client.write_register(6000, 0x4F) # 0x4F = 0000 0000 0100 1111

# # set rising edge to controlword bit 4
# client.write_register(6000, 0x5F) #0x5F = 0000 0000 0101 1111

client.close()

# read_nanotec()
