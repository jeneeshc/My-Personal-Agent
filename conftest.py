import sys
import os

# Add repository root directory to sys.path so tests can import modules seamlessly in CI/CD
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
