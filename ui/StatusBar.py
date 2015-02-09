""" for showing message on status bar"""
from PyQt4.QtGui import QStatusBar, QLabel
import logging, logging.handlers


class StatusLogHandler(logging.Handler):
    """ Logger Handler """
    def __init__(self, status_bar):
        logging.Handler.__init__(self)
        self.status_bar = status_bar

    def emit(self, record):
        self.status_bar.log_message(record.levelno, record.message)

class StatusBar(QStatusBar):
    """ Customized status bar  """
    def __init__(self, parent):
        super(StatusBar, self).__init__(parent)
        logging.handlers.StatusLogHandler = StatusLogHandler
        handler = logging.handlers.StatusLogHandler(self)
        handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(handler)
        self.state_label = QLabel()
        self.addPermanentWidget(self.state_label)

    def log_message(self, level, msg):
        """ show message on status bar """
        self.showMessage(msg)

    def update_state(self, state):
        """ show status info """
        self.state_label.setText(state)
