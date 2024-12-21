import can
import time

CAN_INTERFACE = "vcan0"  
DOOR_STATUS_ID = 0x19b  

def weak_ecu(bus):
  
    door_open = True  
    
    try:
        while True:
            
            door_status = [0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00] if door_open else [0x00, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00] 
            
            msg = can.Message(
                arbitration_id=DOOR_STATUS_ID,
                data=door_status,
                is_extended_id=False
            )
            
            bus.send(msg)
            status_text = "Aperto" if door_open else "Chiuso"
            print(f"Weak ECU: porta {status_text} (ID: {DOOR_STATUS_ID:#X}, data: {door_status})")
            
            # Alterna stato
            door_open = not door_open
            
            # Aspetta 2 secondi
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("Weak ECU interrotto.")
    except can.CanError as e:
        print(f"Errore CAN: {e}")


if __name__ == "__main__":
    with can.interface.Bus(channel="vcan0", bustype="socketcan") as bus:
        weak_ecu(bus)

