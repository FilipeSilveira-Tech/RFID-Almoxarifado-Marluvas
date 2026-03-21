import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_windows import AppRFID

if __name__ == "__main__":
    app = AppRFID()
    app.mainloop()