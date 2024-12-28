import time 
import os 
import sys
import numpy as np
#import scipy as sp


log_file = "dump/noAttackDump.log"

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
        #print(f"Timestamp: {timestamp}, MSG ID: {msg_id}, CAN Message: {can_pld}")

        #store timestamps by id to calculate offsets
        if msg_id not in timestamps_by_id:
            timestamps_by_id[msg_id] = []
        timestamps_by_id[msg_id].append(timestamp)  
#print(f"Timestamps by id: {timestamps_by_id[392]}")        

#calculate offsets of timestamps by id, discard IDs with less than 2 timestamps
offsets_by_id = {}

for msg_id, timestamps in timestamps_by_id.items():
    if len(timestamps) < 2:
        continue
    timestamps = np.array(timestamps, dtype=np.float64)
    
    arrival_times = np.diff(timestamps)
    average_interarrival_time = np.mean(arrival_times)
    
    expectedTime = [timestamps[0] + (i * average_interarrival_time) for i in range(len(timestamps))]
    
    #expectedTime = np.array(expectedTime, dtype=np.float64)

    #print(f"Type : {type(timestamps)}, Shape {timestamps.shape}")
    #print(f"Type : {type(expectedTime)}")

    #for act, exp in zip(timestamps, expectedTime):    
    offset = [act - exp for act, exp in zip(timestamps, expectedTime)]
    offsets_by_id[msg_id] = offset

#print(len(offsets_by_id))
#print(f"Offsets by id: {offsets_by_id[392]}")

#RLS algorithm for clock skew estimation
def rls_updateAlgo (ClockOffset_accum, time, skew_prev, cov_prev, lambda_val = 0.9995): #lambda or "forget factor" is said to be 0.9995 
    time = np.array([[time]])
    G = lambda_val ** -1 * cov_prev @ time / (1 + lambda_val ** -1 * time.T @ cov_prev @ time)
    skew = skew_prev + G.flatten()[0] * (ClockOffset_accum - time.T @ skew_prev)
    cov = lambda_val ** -1 * (cov_prev - G @ time.T @ cov_prev)

    return skew, cov

#print(f"Type: {type(timestamps_by_id[392])}")
#timestampsVal = list(timestamps_by_id.values())
#print(timestampsVal)
timestamps = np.array(timestamps_by_id[392], dtype=np.float64)
offsets = offsets_by_id[392]
cov = np.array([[1.0]])
skew = np.array([[0.0]])

residuals = []

for timestamp, accum_offset in zip(timestamps, offsets):
    skew, cov = rls_updateAlgo(accum_offset, timestamp, skew, cov)
    residual = accum_offset - timestamp * skew
    residuals.append(residual)
    print(f"Updated skew: {skew}")

#the intrusion is detected monitoring the deviation of clock skew

def cumsum (res_err, mean, std_dev, thr): #threshold is said to be 4 or 5
    return max(0, res_err - mean - thr * std_dev)

#print(f"Type: {type(offsets)}")
#print(f"Type: {type(timestamps)}")

threshold = 5
Csum = 0
for res in residuals:
    Csum = cumsum(res, np.mean(residuals), np.std(residuals), threshold)
    if Csum > 5:
        print(f"Intrusion detected! Csum: {Csum}")
        