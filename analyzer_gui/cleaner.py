import pandas as pd
import numpy as np

def clean_and_process_data(input_path: str, output_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(input_path)

        bad_statuses = ['Error', 'Idle']
        df['isValid'] = ~df['Status'].isin(bad_statuses)

        # Replace 0's to prevent division by 0
        df['Current(A)'] = df['Current(A)'].replace(0, np.nan)

        df['Resistance(Ohm)'] = df['Voltage(V)'] / df['Current(A)']

        # Combination of bfill and ffill ensures all NaNs are filled (provided one actual resistance value exists)
        df['Resistance(Ohm)'] = df['Resistance(Ohm)'].bfill().ffill()

        df.to_csv(output_path, index=False)

        return df
    
    except Exception as e:
        print(f"Error in cleaning data: {e}")
        raise