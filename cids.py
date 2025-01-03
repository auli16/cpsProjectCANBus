import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# File log path
log_file = "dump/dump_noAttack.log"

# Existence check
if not os.path.isfile(log_file):
    print(f"Error: {log_file} does not exist.")
    sys.exit(1)

# Specific ID to analyze
selected_msg_id = 0x19B

# Reading log file
timestamps_by_id = {}
with open(log_file) as f:
    for line in f:
        parts = line.strip().split(" ")
        if len(parts) < 3 or not line.startswith("(") or "#" not in parts[2]:
            continue

        try:
            timestamp = float(parts[0].strip("()"))
            msg_id = int(parts[2].split("#")[0], 16)
        except (ValueError, IndexError):
            continue

        if msg_id not in timestamps_by_id:
            timestamps_by_id[msg_id] = []
        timestamps_by_id[msg_id].append(timestamp)

# Check if the selected ID is in the log file
if selected_msg_id not in timestamps_by_id:
    print(f"Error: Selected ID {selected_msg_id} not found in log file.")
    sys.exit(1)

# Offset calculation for the selected ID
timestamps = np.array(timestamps_by_id[selected_msg_id], dtype=np.float64)
if len(timestamps) < 2:
    print(f"Error: Not enough data for ID {selected_msg_id} to calculate offsets.")
    sys.exit(1)

arrival_times = np.diff(timestamps)
average_interarrival_time = np.mean(arrival_times)
expected_time = timestamps[0] + np.arange(len(timestamps)) * average_interarrival_time
offsets = timestamps - expected_time

# RLS
def rls_update_algo(clock_offset_accum, time, skew_prev, cov_prev, lambda_val=0.9995):
    '''
    Recursive Least Squares (RLS) algorithm for clock skew estimation.

    Parameters:
    clock_offset_accum: Accumulated clock offset.
    time: Time value.
    skew_prev: Previous skew value.
    cov_prev: Previous covariance value.
    lambda_val: Forgetting factor.
    '''
    time = np.array([[time]])
    G = lambda_val ** -1 * cov_prev @ time / (1 + lambda_val ** -1 * time.T @ cov_prev @ time) # gain calculation
    skew = skew_prev + G.flatten()[0] * (clock_offset_accum - time.T @ skew_prev)
    cov = lambda_val ** -1 * (cov_prev - G @ time.T @ cov_prev)
    return skew, cov

# Skew and CUSUM
def cusum_control(e, mu_e, sigma_e, L_pos, L_neg, kappa):
    '''
    CUSUM control algorithm for intrusion detection.

    Parameters:
    e: Residual value.
    mu_e: Mean of the residuals.
    sigma_e: Standard deviation of the residuals.
    L_pos: Positive cumulative sum.
    L_neg: Negative cumulative sum.
    kappa: value for making the algorithm more sensitive to changes.
    '''
    sigma_e = max(sigma_e, 1e-3)

    z_score = (e - mu_e) / sigma_e

    L_pos = max(0, L_pos + z_score - kappa)
    L_neg = max(0, L_neg - z_score - kappa)

    return L_pos, L_neg

threshold = 5  
kappa = 1  

cov = np.array([[1.0]])
skew = np.array([[0.0]])
residuals = []

# CUSUM initialization
window_size = 20

recent_offsets = offsets[-window_size:] if len(offsets) >= window_size else offsets
mu_e = np.mean(recent_offsets)
sigma_e = np.std(recent_offsets)

L_pos = 0
L_neg = 0
intrusion_detected = False  

L_pos_values = []
L_neg_values = []
time_values = []

for i, (timestamp, accum_offset) in enumerate(zip(timestamps, offsets), start=1):  
    skew, cov = rls_update_algo(accum_offset, timestamp, skew, cov)
    residual = accum_offset - timestamp * skew
    residuals.append(residual)

    if abs((residual - mu_e) / sigma_e) < 3:
        recent_offsets = offsets[-window_size * i:] if len(offsets) >= window_size * i else offsets
        mu_e = np.mean(recent_offsets)
        sigma_e = np.std(recent_offsets)

    if abs(residual - mu_e) > 0.1 * sigma_e:  
        L_pos, L_neg = cusum_control(residual, mu_e, sigma_e, L_pos, L_neg, kappa)

    L_pos_values.append(L_pos.item() if isinstance(L_pos, np.ndarray) else L_pos)
    L_neg_values.append(L_neg.item() if isinstance(L_neg, np.ndarray) else L_neg)
    time_values.append(timestamp - timestamps[0])
    
    if not intrusion_detected and (L_pos > threshold or L_neg > threshold):
        print(f"Intrusion detected! ID: {selected_msg_id}, L_pos: {L_pos}, L_neg: {L_neg}") # in order to plot the graphics comment this line
        intrusion_detected = True  
        break # in order to plot the graphics comment this line

if not intrusion_detected:
    print(f"No intrusion detected for ID: {selected_msg_id}")

print(L_pos_values)

# in order to plot the graphics, uncomment these lines

'''
plt.figure(figsize=(12, 6))
plt.plot(time_values, L_pos_values, label='L_pos', color='blue')
plt.title('Cumulative Sum (L_pos) vs. Time')
plt.xlabel('Time (s)')
plt.ylabel('L_pos')
plt.grid()
plt.legend()
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(time_values, L_neg_values, label='L_neg', color='red')
plt.title('Cumulative Sum (L_neg) vs. Time')
plt.xlabel('Time (s)')
plt.ylabel('L_neg')
plt.grid()
plt.legend()
plt.show()
'''