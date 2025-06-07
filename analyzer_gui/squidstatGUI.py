import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from plotter import create_voltage_figure, create_current_figure, create_resistance_figure

from cleaner import clean_and_process_data

class SquidstatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Squidstat Data Analyzer")
        self.setGeometry(100, 100, 600, 600)

        self.main_layout = QVBoxLayout()

        self.status_label = QLabel("Select a raw Squidstat CSV file.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.select_button = QPushButton("Select CSV File")
        self.select_button.clicked.connect(self.load_file)

        self.clean_button = QPushButton("Clean and Process Data")
        self.clean_button.clicked.connect(self.clean_data)
        self.clean_button.setEnabled(False)

        self.plot_button = QPushButton("Plot Cleaned Data")
        self.plot_button.clicked.connect(self.plot_data)
        self.plot_button.setEnabled(False)

        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.select_button)
        self.main_layout.addWidget(self.clean_button)
        self.main_layout.addWidget(self.plot_button)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.canvas_voltage = FigureCanvas(plt.figure(figsize=(5, 4)))
        self.canvas_current = FigureCanvas(plt.figure(figsize=(5, 4)))
        self.canvas_resistance = FigureCanvas(plt.figure(figsize=(5, 4)))

        self.tab_widget.addTab(self.canvas_voltage, "Voltage")
        self.tab_widget.addTab(self.canvas_current, "Current")
        self.tab_widget.addTab(self.canvas_resistance, "Resistance")

        self.setLayout(self.main_layout)
        
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
        try:
            if self.df_cleaned is None:
                self.status_label.setText("No cleaned data to plot.")
                return
                
            if hasattr(self, 'tab_widget'):
                self.main_layout.removeWidget(self.tab_widget)
                self.tab_widget.deleteLater()

            self.tab_widget = QTabWidget()
            self.main_layout.addWidget(self.tab_widget)

            df = self.df_cleaned

            figs = {
                "Voltage": create_voltage_figure(df),
                "Current": create_current_figure(self.df_cleaned),
                "Resistance": create_resistance_figure(self.df_cleaned)
            }

            for label, fig in figs.items():
                canvas = FigureCanvas(fig)
                tab = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.addWidget(canvas)
                tab.setLayout(tab_layout)
                self.tab_widget.addTab(tab, label)

            self.status_label.setText("Plots loaded into tabs.")

        except Exception as e:
            self.status_label.setText(f"Plotting failed: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SquidstatGUI()
    gui.show()
    sys.exit(app.exec())