# main.py

import sys
import os
import traceback

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    try:
        print("🚀 Starting Dataset Cleaner Application...")
        # Import inside try to catch import-time errors and avoid package-level side effects
        from presentation_layer.DatasetCleanerUI import DatasetCleanerUI

        app = DatasetCleanerUI()
        # Ensure window close calls on_closing
        if hasattr(app, "on_closing") and callable(getattr(app, "on_closing")):
            app.protocol("WM_DELETE_WINDOW", app.on_closing)
        else:
            # Fallback: use default destroy to ensure graceful exit
            app.protocol("WM_DELETE_WINDOW", app.destroy)

        print("✅ UI initialized — entering mainloop")
        app.mainloop()
        print("👋 Application closed cleanly.")
    except Exception as e:
        print("❌ Failed to start application. Full traceback follows:\n")
        traceback.print_exc()
        # Pause so user can see the error when run from double-click / terminal
        try:
            input("\nPress Enter to exit...")
        except Exception:
            pass

if __name__ == "__main__":
    main()
