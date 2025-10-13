import sys
from PyQt6.QtWidgets import QApplication
from modules import MainWindow
from modules import Console
from modules import Parameters
import helpers

def main():
    params = Parameters()

    # Check if the console is attached
    if not helpers.has_console() or params.get_param_value('gui'):
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec()
        sys.exit()
    else:
        app = Console()
        app.run(params=params)

if __name__ == "__main__":
    main()