# debug_main.py
import sys
import os
import traceback

def test_imports():
    modules = [
        'tkinter',
        'pandas',
        'numpy', 
        'matplotlib',
        'sklearn',
        'mysql.connector',
        'scipy'
    ]
    
    print("Testing imports...")
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    print("\nTesting application modules...")
    app_modules = [
        'presentation_layer.DatasetCleanerUI',
        'business_layer.DataCleaningController', 
        'data_layer.DatasetManager',
        'models'
    ]
    
    for module in app_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    test_imports()
    
    print("\n" + "="*50)
    print("Attempting to start main application...")
    print("="*50)
    
    try:
        from main import main
        main()
    except Exception as e:
        print(f"Failed to start: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")