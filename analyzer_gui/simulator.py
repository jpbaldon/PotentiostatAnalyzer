from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import random
import time

class RealTimeSimulator(QObject):
    data_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._data = {'time': [], 'voltage': [], 'current': [], 'resistance': []}
        self._start_time = None
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.generate_data)

    def run(self):
        self._data = {'time': [], 'voltage': [], 'current': [], 'resistance': []}
        self._start_time = time.time()
        self.timer.start()

    def generate_data(self):
        elapsed = time.time() - self._start_time
        if elapsed >= 30:
            self.timer.stop()
            self.finished_signal.emit()
            return
    
        self._data['time'].append(elapsed)
        self._data['voltage'].append(random.uniform(0, 5))
        self._data['current'].append(random.uniform(-0.01, 0.01))
        self._data['resistance'].append(random.uniform(1000,10000))

        self.data_signal.emit(self._data.copy())


    def stop(self):
        self.timer.stop()
        self.finished_signal.emit()