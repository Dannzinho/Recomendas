import sys
import os
import tkinter as tk
from src.database.db_manager import DBManager
from src.utils.recommendation_manager import RecommendationManager
from src.ui.gui_interface import RecomendasGUI
from src.data.initial_data_loader import load_initial_data 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

if __name__ == '__main__':
 
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['PGCLIENTENCODING'] = 'UTF8'

    db_manager = DBManager()

    load_initial_data(db_manager) 

    recommendation_manager = RecommendationManager(db_manager)
    
    root = tk.Tk()
    app = RecomendasGUI(root, db_manager, recommendation_manager)
    root.mainloop()