import pandas as pd
from matplotlib.figure import Figure
import argparse

from matplotlib.backends.backend_agg import FigureCanvasAgg

def load_cleaned_data(csv_path):
    return pd.read_csv(csv_path)

def create_voltage_figure(df) -> Figure:
    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    ax.plot(df['Time(s)'], df['Voltage(V)'], label='Voltage (V)', color='blue')
    ax.set_title('Voltage vs Time')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (V)')
    ax.grid(True)
    fig.tight_layout()
    return fig

def create_current_figure(df) -> Figure:
    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    ax.plot(df['Time(s)'], df['Current(A)'], color='green')
    ax.set_title("Current vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Current (A)")
    ax.grid(True)
    fig.tight_layout()
    return fig

def create_resistance_figure(df) -> Figure:
    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    if 'Resistance(Ohm)' not in df.columns:
        df['Resistance(Ohm)'] = df['Voltage(V)'] / df['Current(A)']

    ax.plot(df['Time(s)'], df['Resistance(Ohm)'], label='Resistance (Ω)', color='red')
    ax.set_title("Resistance vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Resistance (Ω)")
    ax.grid(True)
    fig.tight_layout()
    return fig

def highlight_anomalies(df):
    df = df.copy()
    if 'isValid' in df.columns:
        df['Anomaly'] = ~df['isValid'] | (df['Status'] != 'Measuring')
    else:
        df['Anomaly'] = df['Status'] != 'Measuring'
    return df

def render_figure_cli(fig: Figure):
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    fig.savefig(f"{fig.axes[0].get_title().replace(' ', '_')}.png")
    print(f"Saved: {fig.axes[0].get_title()}.png")

def plot_all_cli(df):
    for fig in [create_voltage_figure(df), create_current_figure(df), create_resistance_figure(df)]:
        render_figure_cli(fig)

def main():
    parser = argparse.ArgumentParser(description="Plot cleaned Squidstat CSV data.")
    parser.add_argument('csv_path', help="Path to cleaned CSV file")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.csv_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    plot_all_cli(df)

if __name__ == "__main__":
    main()
