import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from src.algorithms.content_based import load_products, calculate_similarity, get_recommendations_content_based
from src.algorithms.collaborative import load_feedback, create_user_item_matrix, calculate_user_similarity, get_collaborative_recommendations, load_users
from src.utils.recommendation_manager import RecommendationHistoryManager
from src.utils.metrics import load_interactions, calculate_click_count, calculate_acceptance_rate, get_feedback_summary
from src.ui.cli_interface import main_cli

def main():
    print("Bem-vindo ao Recomendas!")
    print("Escolha a interface:")
    print("1. Interface de Linha de Comando (CLI)")
    print("2. Interface Gráfica (GUI)")

    interface_choice = input("Digite sua escolha (1 ou 2): ").strip()

    if interface_choice == '1':
        print("\nIniciando a Interface de Linha de Comando...")
        main_cli()
    elif interface_choice == '2':
        try:
            from src.ui.gui_interface import RecomendasGUI
            import tkinter as tk
            print("\nIniciando a Interface Gráfica...")
            root = tk.Tk()
            app = RecomendasGUI(root)
            root.mainloop()
        except ImportError:
            print("\nInterface Gráfica não encontrada ou com erros. Iniciando a Interface de Linha de Comando.")
            main_cli()
    else:
        print("Escolha inválida. Iniciando a Interface de Linha de Comando por padrão.")
        main_cli()

if __name__ == '__main__':
    main()