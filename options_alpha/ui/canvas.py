"""
Matplotlib canvas implementation for Options Alpha Analyzer
Used for all charting and visualization functionality
"""

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy

class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for embedding charts in Qt windows"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Initialize the canvas with the given dimensions"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry() 