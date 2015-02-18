from PyQt4.QtCore import QSettings

SETTINGS = QSettings('c0deforfun', 'lll')

def save_run_config(prog, args, work_dir):
    print('save: %s, %s %s') %(prog, args, work_dir)

