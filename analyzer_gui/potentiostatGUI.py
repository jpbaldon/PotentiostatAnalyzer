import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTabWidget
)
from PyQt6.QtCore import (Qt)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from plotter import create_voltage_figure, create_current_figure, create_resistance_figure

from cleaner import clean_and_process_data

from simulator import RealTimeSimulator



class potentiostatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Potentiostat Data Analyzer")
        self.setGeometry(100, 100, 800, 700)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.sim_tab = QWidget()
        sim_layout = QVBoxLayout()
        self.sim_tab.setLayout(sim_layout)

        self.start_sim_button = QPushButton("Start Simulation")
        self.stop_sim_button = QPushButton("Stop Simulation")
        self.stop_sim_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_sim_button)
        button_layout.addWidget(self.stop_sim_button)

        sim_layout.addLayout(button_layout)

        self.sim_plot_tabs = QTabWidget()
        sim_layout.addWidget(self.sim_plot_tabs)

        self.sim_canvas_voltage = FigureCanvas(plt.figure(figsize=(5,4)))
        self.sim_canvas_current = FigureCanvas(plt.figure(figsize=(5,4)))
        self.sim_canvas_resistance = FigureCanvas(plt.figure(figsize=(5,4)))

        self.sim_plot_tabs.addTab(self.sim_canvas_voltage, "Voltage")
        self.sim_plot_tabs.addTab(self.sim_canvas_current, "Current")
        self.sim_plot_tabs.addTab(self.sim_canvas_resistance, "Resistance")

        self.tab_widget.addTab(self.sim_tab, "Live Simulation")

        self.start_sim_button.clicked.connect(self.start_simulation)
        self.stop_sim_button.clicked.connect(self.stop_simulation)

        self.data_tab = QWidget()
        data_layout = QVBoxLayout()
        self.data_tab.setLayout(data_layout)

        self.status_label = QLabel("Select a raw potentiostat CSV file.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.select_button = QPushButton("Select CSV File")
        self.select_button.clicked.connect(self.load_file)

        self.clean_button = QPushButton("Clean and Process Data")
        self.clean_button.clicked.connect(self.clean_data)
        self.clean_button.setEnabled(False)

        self.plot_button = QPushButton("Plot Cleaned Data")
        self.plot_button.clicked.connect(self.plot_data)
        self.plot_button.setEnabled(False)

        for widget in [self.status_label, self.select_button, self.clean_button, self.plot_button]:
            data_layout.addWidget(widget)

        self.plot_tabs = QTabWidget()
        data_layout.addWidget(self.plot_tabs)

        self.canvas_voltage = FigureCanvas(plt.figure(figsize=(5, 4)))
        self.canvas_current = FigureCanvas(plt.figure(figsize=(5, 4)))
        self.canvas_resistance = FigureCanvas(plt.figure(figsize=(5, 4)))

        self.plot_tabs.addTab(self.canvas_voltage, "Voltage")
        self.plot_tabs.addTab(self.canvas_current, "Current")
        self.plot_tabs.addTab(self.canvas_resistance, "Resistance")

        self.tab_widget.addTab(self.data_tab, "Data Loader")

        self.sim_thread = None
        self.output_path = None

        self.input_path = None
        self.output_path = None
        self.df_cleaned = None

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "./sample_data", "CSV Files (*.csv)"
        )
        if file_name:
            self.input_path = file_name
            self.output_path = os.path.join("output", os.path.basename(file_name).replace(".csv", "_cleaned.csv"))
            self.status_label.setText(f"Loaded file: {os.path.basename(file_name)}")
            self.clean_button.setEnabled(True)

    def clean_data(self):
        try:
            self.df_cleaned = clean_and_process_data(self.input_path, self.output_path)
            self.status_label.setText("Data cleaned successfully!")
            self.plot_button.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def plot_data(self):
        if self.df_cleaned is None:
            self.status_label.setText("No cleaned data to plot.")
            return
        try:
            self.plot_tabs.clear()

            df = self.df_cleaned
            figs = {
                "Voltage": create_voltage_figure(df),
                "Current": create_current_figure(df),
                "Resistance": create_resistance_figure(df),
            }

            for label, fig in figs.items():
                canvas = FigureCanvas(fig)
                tab = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.addWidget(canvas)
                tab.setLayout(tab_layout)
                self.plot_tabs.addTab(tab, label)

            self.status_label.setText("Plots loaded into tabs.")

        except Exception as e:
            self.status_label.setText(f"Plotting failed: {str(e)}")

    def start_simulation(self):
        if self.sim_thread is not None:
            self.status_label.setText("Simulation already running")
            return
        
        self.simulator = RealTimeSimulator()
        self.simulator.data_signal.connect(self.update_sim_plots)
        self.simulator.finished_signal.connect(self.simulation_finished)
        self.simulator.run()

        self.start_sim_button.setEnabled(False)
        self.stop_sim_button.setEnabled(True)
        self.status_label.setText("Simulation started")

    def stop_simulation(self):
        if self.simulator:
            self.simulator.stop()
        self.stop_sim_button.setEnabled(False)
        self.status_label.setText("Stopping simulation...")

    def simulation_finished(self):
        self.sim_thread = None
        self.simulator = None
        self.start_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)
        self.status_label.setText("Simulation stopped")

    def update_sim_plots(self, data):
        try:
            for canvas, key in zip(
                [self.sim_canvas_voltage, self.sim_canvas_current, self.sim_canvas_resistance],
                ['voltage','current','resistance']
            ):
                fig = canvas.figure
                fig.clear()
                ax = fig.add_subplot(111)
                ax.plot(data['time'], data[key])
                ax.set_title(f"Live {key.capitalize()}")
                ax.set_xlabel("Time (s)")
                ax.set_ylabel(key.capitalize())
                fig.tight_layout()
                canvas.draw()
        except Exception as e:
            self.status_label.setText(f"Error updating simulation plots: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = potentiostatGUI()
    gui.show()
    sys.exit(app.exec())