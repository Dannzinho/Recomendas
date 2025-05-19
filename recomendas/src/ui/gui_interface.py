import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from PIL import Image, ImageTk
import json
from src.algorithms.content_based import load_products, calculate_similarity, get_recommendations_content_based
from src.algorithms.collaborative import load_feedback, create_user_item_matrix, calculate_user_similarity, get_collaborative_recommendations, load_users
from src.utils.recommendation_manager import RecommendationHistoryManager
from src.utils.metrics import load_interactions, calculate_click_count, calculate_acceptance_rate, get_feedback_summary

class RecomendasGUI:
    def __init__(self, master):
        self.master = master
        master.title("Recomendas - Sistema de Recomendação")

        try:
            img = Image.open("src/ui/logo.png") 
            img = img.resize((500, 300))
            self.logo = ImageTk.PhotoImage(img)
            self.logo_label = tk.Label(master, image=self.logo)
            self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)
        except FileNotFoundError:
            print("Logo não encontrada.")
            self.logo_label = ttk.Label(master, text="Recomendas")
            self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.products_df = load_products()
        with open("src/data/users.json", 'r') as f:
            self.users_data = json.load(f)
        self.feedback_df = load_feedback()
        self.interactions = load_interactions()
        self.history_manager = RecommendationHistoryManager()

        self.cosine_sim = calculate_similarity(self.products_df.copy())
        self.user_item_matrix, self.user_ids, self.product_ids = create_user_item_matrix(self.feedback_df)
        self.user_similarity, _ = calculate_user_similarity(self.user_item_matrix)

        self.user_label = ttk.Label(master, text="ID do Usuário:")
        self.user_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.user_entry = ttk.Entry(master)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.register_button = ttk.Button(master, text="Cadastrar Usuário", command=self.register_user)
        self.register_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.recommendation_label = ttk.Label(master, text="Recomendações:")
        self.recommendation_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.recommendation_text = scrolledtext.ScrolledText(master, height=10, width=50)
        self.recommendation_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        self.recommendation_text.config(state=tk.DISABLED)

        self.history_label = ttk.Label(master, text="Histórico de Recomendações:")
        self.history_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.history_text = scrolledtext.ScrolledText(master, height=5, width=50)
        self.history_text.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
        self.history_text.config(state=tk.DISABLED)

        self.content_button = ttk.Button(master, text="Recomendar (Conteúdo)", command=self.get_content_recommendations)
        self.content_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        self.collaborative_button = ttk.Button(master, text="Recomendar (Colaborativo)", command=self.get_collaborative_recommendations)
        self.collaborative_button.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.history_button = ttk.Button(master, text="Ver Histórico", command=self.show_history)
        self.history_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.metrics_button = ttk.Button(master, text="Ver Métricas", command=self.show_metrics)
        self.metrics_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(3, weight=1)
        master.grid_rowconfigure(4, weight=1)

    def register_user(self):
        register_window = tk.Toplevel(self.master)
        register_window.title("Cadastro de Usuário")

        name_label = ttk.Label(register_window, text="Nome:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(register_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        email_label = ttk.Label(register_window, text="Email:")
        email_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        email_entry = ttk.Entry(register_window)
        email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        def save_user():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            if name and email:
                new_user = {"user_id": email.split('@')[0], "name": name, "email": email, "purchase_history": []}
                self.users_data.append(new_user)
                with open("src/data/users.json", 'w') as f:
                    json.dump(self.users_data, f, indent=2)
                messagebox.showinfo("Sucesso", f"Usuário '{name}' cadastrado com ID '{new_user['user_id']}'.")
                register_window.destroy()
            else:
                messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

        save_button = ttk.Button(register_window, text="Salvar", command=save_user)
        save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        register_window.grid_columnconfigure(1, weight=1)

    def get_content_recommendations(self):
        user_id = self.user_entry.get().strip()
        if not user_id:
            messagebox.showerror("Erro", "Por favor, insira o ID do usuário.")
            return

        user = next((u for u in self.users_data if u['user_id'] == user_id), None)
        if not user:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return

        recommendations = get_recommendations_content_based(user_id, self.products_df, self.cosine_sim, self.users_data)
        self.display_recommendations(user_id, recommendations, "baseadas em conteúdo")

    def get_collaborative_recommendations(self):
        user_id = self.user_entry.get().strip()
        if not user_id:
            messagebox.showerror("Erro", "Por favor, insira o ID do usuário.")
            return

        if self.user_ids and user_id in self.user_ids:
            recommendations = get_collaborative_recommendations(user_id, self.user_item_matrix, self.user_similarity, self.user_ids, self.product_ids)
            self.display_recommendations(user_id, recommendations, "colaborativas")
        else:
            messagebox.showinfo("Info", "Não há dados suficientes para recomendações colaborativas para este usuário.")

    def display_recommendations(self, user_id, recommendations, method):
        self.recommendation_text.config(state=tk.NORMAL)
        self.recommendation_text.delete(1.0, tk.END)
        if recommendations:
            self.recommendation_text.insert(tk.END, f"Recomendações {method} para o usuário {user_id}:\n")
            for rec_id in recommendations:
                product = self.products_df[self.products_df['product_id'] == rec_id].iloc[0]
                self.recommendation_text.insert(tk.END, f"- {product['name']} ({rec_id})\n")
                self.history_manager.add_recommendation(user_id, rec_id)
        else:
            self.recommendation_text.insert(tk.END, f"Não há recomendações {method} para o usuário {user_id} no momento.\n")
        self.recommendation_text.config(state=tk.DISABLED)
        self.show_history()

    def show_history(self):
        user_id = self.user_entry.get().strip()
        if user_id:
            history = self.history_manager.get_history(user_id)
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            if history:
                self.history_text.insert(tk.END, f"Histórico de recomendações para o usuário {user_id}:\n")
                for product_id in history:
                    product = self.products_df[self.products_df['product_id'] == product_id].iloc[0]
                    self.history_text.insert(tk.END, f"- {product['name']} ({product_id})\n")
            else:
                self.history_text.insert(tk.END, f"Nenhum histórico de recomendações encontrado para o usuário {user_id}.\n")
            self.history_text.config(state=tk.DISABLED)
        else:
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(tk.END, "Por favor, insira o ID do usuário para ver o histórico.\n")
            self.history_text.config(state=tk.DISABLED)

    def show_metrics(self):
        user_id = self.user_entry.get().strip()
        if not user_id:
            messagebox.showerror("Erro", "Por favor, insira o ID do usuário para ver as métricas.")
            return

        user_interactions = [i for i in self.interactions if i.get('user_id') == user_id]
        feedback_count = len([f for f in self.feedback_df.to_dict('records') if f.get('user_id') == user_id])
        click_count = calculate_click_count(user_interactions)
        acceptance_count = len([i for i in user_interactions if i.get('type') == 'accept'])
        total_interactions = len(user_interactions)
        acceptance_rate = (acceptance_count / total_interactions) * 100 if total_interactions > 0 else 0

        metrics_message = f"Métricas para o usuário {user_id}:\n"
        metrics_message += f"  Feedbacks dados: {feedback_count}\n"
        metrics_message += f"  Cliques realizados: {click_count}\n"
        metrics_message += f"  Taxa de aceitação (aproximada): {acceptance_rate:.2f}%\n"

        messagebox.showinfo("Métricas", metrics_message)

if __name__ == '__main__':
    root = tk.Tk()
    app = RecomendasGUI(root)
    root.mainloop()