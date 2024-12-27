import os
import sys
import numpy as np

# Path del file log
log_file = "dump/dump_masq.log"

# Verifica se il file esiste
if not os.path.isfile(log_file):
    print(f"Error: {log_file} does not exist.")
    sys.exit(1)

# Lettura del file log
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

# Calcolo degli offset
offsets_by_id = {}
for msg_id, timestamps in timestamps_by_id.items():
    if len(timestamps) < 2:
        continue
    timestamps = np.array(timestamps, dtype=np.float64)
    arrival_times = np.diff(timestamps)
    average_interarrival_time = np.mean(arrival_times)
    expected_time = timestamps[0] + np.arange(len(timestamps)) * average_interarrival_time
    offsets_by_id[msg_id] = timestamps - expected_time

# Algoritmo RLS
def rls_update_algo(clock_offset_accum, time, skew_prev, cov_prev, lambda_val=0.9995):
    time = np.array([[time]])
    G = lambda_val ** -1 * cov_prev @ time / (1 + lambda_val ** -1 * time.T @ cov_prev @ time)
    skew = skew_prev + G.flatten()[0] * (clock_offset_accum - time.T @ skew_prev)
    cov = lambda_val ** -1 * (cov_prev - G @ time.T @ cov_prev)
    return skew, cov

# Calcolo skew e rilevamento intrusioni con CUSUM
def cusum_control(e, mu_e, sigma_e, L_pos, L_neg, kappa):
    sigma_e = max(sigma_e, 1e-3)


    z_score = (e - mu_e) / sigma_e

    # Aggiornamento L+ e L-
    L_pos = max(0, L_pos + z_score - kappa)
    L_neg = max(0, L_neg - z_score - kappa)

    return L_pos, L_neg

threshold = 4  # Maggiore per ridurre falsi positivi
kappa = 2  # Più sensibile al rumore

# Elaborazione specifica per l'ID 411
msg_id = 149
if msg_id in offsets_by_id:
    offsets = offsets_by_id[msg_id]
    timestamps = np.array(timestamps_by_id[msg_id], dtype=np.float64)
    cov = np.array([[1.0]])
    skew = np.array([[0.0]])
    residuals = []

    # Inizializzazione di CUSUM
    if len(offsets) > 0:
        mu_e = np.mean(offsets[:min(10, len(offsets))])  # Calcolo iniziale su primi valori
        sigma_e = np.std(offsets[:min(10, len(offsets))])
    else:
        mu_e = 0
        sigma_e = 1

    L_pos = 0
    L_neg = 0

    for timestamp, accum_offset in zip(timestamps, offsets):
        skew, cov = rls_update_algo(accum_offset, timestamp, skew, cov)
        residual = accum_offset - timestamp * skew
        residuals.append(residual)

        # Debugging
        print(f"Residual: {residual}, Mu_e: {mu_e}, Sigma_e: {sigma_e}, L_pos: {L_pos}, L_neg: {L_neg}")

        # Aggiornamento di mu_e e sigma_e se il valore è normale
        if sigma_e == 0:
            sigma_e = 1e-6  # Prevenzione divisione per zero

        if abs((residual - mu_e) / sigma_e) < 3:
            mu_e = np.mean(offsets[:10]) if len(offsets) >= 10 else np.mean(offsets)
            sigma_e = np.std(offsets[:10]) if len(offsets) >= 10 else np.std(offsets)


        # Aggiornamento di L+ e L-
        if abs(residual - mu_e) > 0.1 * sigma_e:  # Soglia basata sulla deviazione standard
            L_pos, L_neg = cusum_control(residual, mu_e, sigma_e, L_pos, L_neg, kappa)

        # Verifica intrusioni
        if L_pos > threshold or L_neg > threshold:
            print(f"Intrusion detected! ID: {msg_id}, L_pos: {L_pos}, L_neg: {L_neg}")
            L_pos = 0
            L_neg = 0
            break
else:
    print(f"ID {msg_id} not found in the data.")
