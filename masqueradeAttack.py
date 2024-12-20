import can
import time
import math

CAN_INTERFACE = "vcan0"  
DOOR_STATUS_ID = 0x19b  

def takeTime(bus, t, id):

    start_time = time.time()
    timestamps = []

    try:
        while time.time()- start_time < t:
            msg = bus.recv(timeout=1)
            if msg is not None and msg.arbitration_id == id:
                timestamps.append(msg.timestamp)
    except Exception as e:
        print("eccezione")
    
    sumDif = 0
    for i in range(1, len(timestamps)):
        sumDif += timestamps[i] - timestamps[i-1]
    return sumDif/(len(timestamps) - 1)

def masq_attack(bus):
    time = takeTime(bus, 20, DOOR_STATUS_ID)
    '''
    prendere l'ultimo timestamp e iniziare a inviare i messaggi time secondi dopo ogni time secondi
    '''






if __name__ == "__main__":
    with can.interface.Bus(channel="vcan0", bustype="socketcan") as bus:

        
