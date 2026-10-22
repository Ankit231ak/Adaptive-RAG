"""
Alias shim linking train_router.py to train_controller.py (Blueprint Section 15).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.train_controller import train_controller

if __name__ == "__main__":
    train_controller()
