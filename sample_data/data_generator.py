import csv
import numpy as np
import random

def simulate_squidstat_data(filename='simulated_squidstat.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Time(s)', 'Voltage(V)', 'Current(A)', 'Cycle', 'Step', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        time = 0.0
        dt = 0.1
        step = 1
        for i in range(100):
            voltage = 0.2 * np.sin(0.1 * i)
            current = 0.01 * np.cos(0.1 * i)

            voltage += np.random.normal(0, 0.005)
            current += np.random.normal(0, 0.0005)

            r = random.random()
            if r < 0.85:
                status = 'Measuring'
            elif r < 0.95:
                status = 'Idle'
            else:
                status = 'Error'

            writer.writerow({
                'Time(s)': round(time, 2),
                'Voltage(V)': round(voltage, 5),
                'Current(A)': round(current, 7),
                'Cycle': 1,
                'Step': step,
                'Status': status
            })

            time += dt

    print(f"Simulated data with noise and status saved to {filename}")

simulate_squidstat_data()