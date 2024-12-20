import time 
import os 
import sys
#import numpy as np
#import scipy as sp


log_file = "candump-2024-12-19_153802.log"

if not os.path.isfile(log_file):
    print(f"Error: {log_file} does not exist.")
    sys.exit(1)
#open file and read lines, extract timestamp, id and payload
with open (log_file) as f:
    lines = f.readlines()
    timestamps_by_id = {}
    for line in lines:
        parts = line.strip().split(" ")
        if len(parts) < 3:
            continue

        timestamp = parts[0].strip("()")
        msg_id = parts[2].split("#")[0]
        msg_id = int(msg_id, 16)
        can_pld = parts[2].split("#")[1]
        print(f"Timestamp: {timestamp}, MSG ID: {msg_id}, CAN Message: {can_pld}")

        #store timestamps by id to calculate offsets
        if msg_id not in timestamps_by_id:
            timestamps_by_id[msg_id] = []
        timestamps_by_id[msg_id].append(timestamp)  
        
print(timestamps_by_id[392])




