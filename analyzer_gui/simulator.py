from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import random

class RealTimeSimulator(QObject):
    data_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._data = {'voltage': [], 'current': [], 'resistance': []}
        self._t = 0
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.generate_data)

    def run(self):
        self._t = 0
        self._data = {'voltage': [], 'current': [], 'resistance': []}
        self.timer.start()

    def generate_data(self):
        if self._t >= 100:
            self.timer.stop()
            self.finished_signal.emit()
            return
    
        self._t += 1
        self._data['voltage'].append(random.uniform(0, 5))
        self._data['current'].append(random.uniform(-0.01, 0.01))
        self._data['resistance'].append(random.uniform(1000,10000))

        self.data_signal.emit(self._data.copy())


    def stop(self):
        self.timer.stop()
        self.finished_signal.emit()