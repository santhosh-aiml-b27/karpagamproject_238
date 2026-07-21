"""
EcoRoute AI - Environment Verification Script
"""

import sys

def check_environment():
    print("=" * 55)
    print("      ECOROUTE AI ENVIRONMENT VERIFICATION      ")
    print("=" * 55)
    print(f"Python Version     : {sys.version.split()[0]}")
    
    packages = [
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("Scikit-Learn", "sklearn"),
        ("TensorFlow", "tensorflow"),
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Matplotlib", "matplotlib"),
    ]
    
    all_ok = True
    for name, module_name in packages:
        try:
            mod = __import__(module_name)
            version = getattr(mod, "__version__", "Installed")
            print(f"{name:<18}: {version}")
        except ImportError:
            print(f"{name:<18}: NOT INSTALLED")
            all_ok = False
            
    print("=" * 55)
    if all_ok:
        print("STATUS: All essential libraries imported successfully!")
    else:
        print("STATUS: Some packages are missing. Please run `pip install -r requirements.txt`.")
    print("=" * 55)

if __name__ == "__main__":
    check_environment()
