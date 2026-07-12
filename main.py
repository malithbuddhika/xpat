"""Entry point for XPAT Worker Automation Tool."""

import faulthandler
from app.gui.main_window import main


if __name__ == "__main__":
    faulthandler.enable()
    main()
