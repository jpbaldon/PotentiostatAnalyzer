import os
import pandas as pd
import tempfile
from analyzer_gui.cleaner import clean_and_process_data

def test_cleaner_handles_valid_data():
    sample_data = """Time(s),Voltage(V),Current(A),Cycle,Step,Status
    0.0,0.1,0.01,1,1,Measuring
    0.1,0.2,0.02,1,1,Measuring
    0.2,0.3,0.00,1,1,Error
    0.3,0.4,0.04,1,1,Idle"""

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv") as f:
        f.write(sample_data)
        input_path = f.name

    output_path = input_path.replace(".csv", "_out.csv")

    df_cleaned = clean_and_process_data(input_path, output_path)

    df_saved = pd.read_csv(output_path)

    assert 'Resistance(Ohm)' in df_cleaned.columns
    assert 'isValid' in df_cleaned.columns
    assert df_cleaned.shape[0] == 4

    assert df_cleaned.iloc[0]['isValid'] == True
    assert df_cleaned.iloc[2]['isValid'] == False
    assert pd.notna(df_cleaned.iloc[1]['Resistance(Ohm)'])
    assert pd.notna(df_cleaned.iloc[0]['Resistance(Ohm)'])

    os.remove(input_path)
    os.remove(output_path)
