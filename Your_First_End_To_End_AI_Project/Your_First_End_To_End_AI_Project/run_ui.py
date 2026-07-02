"""
run_ui.py — Streamlit launcher
Run with: streamlit run run_ui.py
Or: streamlit run app/ui/streamlit_app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# This file exists so you can run: streamlit run run_ui.py
# It re-exports the Streamlit app
from app.ui.streamlit_app import main
main()
