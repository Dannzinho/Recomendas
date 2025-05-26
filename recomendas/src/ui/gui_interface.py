import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from PIL import Image, ImageTk
import re
import uuid
import bcrypt
import webbrowser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db_manager import DBManager, User, Product, Feedback, Interaction, Category
from src.algorithms.content_based import ContentBasedRecommender
from src.utils.recommendation_manager import RecommendationManager

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete(self, key):
        current_node = self.head
        if current_node and current_node.data == key:
            self.head = current_node.next
            current_node = None
            return

        prev_node = None
        while current_node and current_node.data != key:
            prev_node = current_node
            current_node = current_node.next

        if current_node is None:
            return

        prev_node.next = current_node.next
        current_node = None

    def search(self, key):
        current_node = self.head
        while current_node:
            if current_node.data == key:
                return current_node
            current_node = current_node.next
        return None

    def get_all(self):
        elements = []
        current_node = self.head
        while current_node:
            elements.append(current_node.data)
            current_node = current_node.next
        return elements

    def is_empty(self):
        return self.head is None

    def __len__(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count

    def __str__(self):
        nodes = []
        current = self.head
        while current:
            nodes.append(str(current.data))
            current = current.next
        return ' -> '.join(nodes)

    def get_last_item(self):
        if not self.head:
            return None
        current_node = self.head
        while current_node.next:
            current_node = current_node.next
        return current_node.data


class RecomendasGUI:
    def __init__(self, master, db_manager, recommendation_manager):
        self.master = master
        master.title("Recomendas - Sistema de Recomendação")
        master.geometry("1200x800")
        master.resizable(True, True)

        self.db_manager = db_manager
        self.recommendation_manager = recommendation_manager

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.text_color = "#ecf0f1"
        self.accent_color = "#e74c3c"
        self.font_header = ("Helvetica", 16, "bold")
        self.font_body = ("Helvetica", 12)
        self.font_button = ("Helvetica", 10, "bold")

        self.master.tk_setPalette(background=self.secondary_color, foreground=self.text_color,
                                   activeBackground=self.primary_color, activeForeground="white")

        self.current_user = None

        self.user_interests_options = [
            "Eletrodomésticos", "TVs", "Smartphones", "Livros",
            "Tênis", "Video Games"
        ]
        self.selected_interest = tk.StringVar(master)
        self.selected_interest.set(self.user_interests_options[0])

        self.book_genres_options = [
            "Romance", "Suspense", "Fantasia", "Ficção Científica"
        ]
        self.selected_book_genre = tk.StringVar(master)
        self.selected_book_genre.set(self.book_genres_options[0])

        self.tennis_type_options = [
            "Esportivo", "Casual"
        ]
        self.selected_tennis_type = tk.StringVar(master)
        self.selected_tennis_type.set(self.tennis_type_options[0])

        self.home_appliances_options = [
            "Geladeiras", "Fogões", "Lava e seca"
        ]
        self.selected_home_appliance_type = tk.StringVar(master)
        self.selected_home_appliance_type.set(self.home_appliances_options[0])

        self.smartphone_brand_options = [
            "Apple", "Samsung", "Google", "Xiaomi"
        ]
        self.selected_smartphone_brand = tk.StringVar(master)
        self.selected_smartphone_brand.set(self.smartphone_brand_options[0])

        self.selected_new_interest = tk.StringVar(master)
        self.selected_new_interest.set(self.user_interests_options[0])

        self.new_book_genre = tk.StringVar(master)
        self.new_book_genre.set(self.book_genres_options[0])

        self.new_tennis_type = tk.StringVar(master)
        self.new_tennis_type.set(self.tennis_type_options[0])

        self.new_home_appliance_type = tk.StringVar(master)
        self.new_home_appliance_type.set(self.home_appliances_options[0])

        self.new_smartphone_brand = tk.StringVar(master)
        self.new_smartphone_brand.set(self.smartphone_brand_options[0])


        self.recent_views = LinkedList()
        self.MAX_RECENT_VIEWS = 5

        self.create_login_frame()

    def create_login_frame(self):
        self.clear_frame()
        self.login_frame = ttk.Frame(self.master, padding="30 20 30 20", style='Dark.TFrame')
        self.login_frame.pack(expand=True, fill='both')

        self.style.configure('Dark.TFrame', background=self.secondary_color)
        self.style.configure('Dark.TLabel', background=self.secondary_color, foreground=self.text_color, font=self.font_header)
        self.style.configure('Dark.TEntry', fieldbackground="#3b526b", foreground="white", borderwidth=1, relief="solid")
        self.style.map('Dark.TButton', background=[('active', self.primary_color)], foreground=[('active', 'white')])
        self.style.configure('TCombobox', fieldbackground="#3b526b", foreground="white", selectbackground=self.primary_color, selectforeground="white")
        self.style.map('TCombobox', fieldbackground=[('readonly', "#3b526b")])

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))
        try:
            img = Image.open(logo_path)
            img = img.resize((500, 400), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(self.login_frame, image=self.logo_img, background=self.secondary_color)
            logo_label.pack(pady=20)
        except FileNotFoundError:
            print(f"Logo not found at {logo_path}")
            logo_label = ttk.Label(self.login_frame, text="Recomendas Logo", style='Dark.TLabel')
            logo_label.pack(pady=20)

        ttk.Label(self.login_frame, text="Login", style='Dark.TLabel').pack(pady=10)

        username_label = ttk.Label(self.login_frame, text="Usuário:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30, style='Dark.TEntry')
        self.username_entry.pack(pady=5)

        password_label = ttk.Label(self.login_frame, text="Senha:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30, style='Dark.TEntry')
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_frame, text="Entrar", command=self.login, style='Dark.TButton').pack(pady=10)
        ttk.Button(self.login_frame, text="Cadastrar", command=self.create_register_frame, style='Dark.TButton').pack(pady=5)

    def create_register_frame(self):
        self.clear_frame()
        self.register_frame = ttk.Frame(self.master, padding="30 20 30 20", style='Dark.TFrame')
        self.register_frame.pack(expand=True, fill='both')

        ttk.Label(self.register_frame, text="Cadastro", style='Dark.TLabel').pack(pady=10)

        username_label = ttk.Label(self.register_frame, text="Usuário:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        username_label.pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.register_frame, width=30, style='Dark.TEntry')
        self.reg_username_entry.pack(pady=5)

        contact_label = ttk.Label(self.register_frame, text="Contato (Email ou Telefone):", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        contact_label.pack(pady=5)
        self.reg_contact_entry = ttk.Entry(self.register_frame, width=30, style='Dark.TEntry')
        self.reg_contact_entry.pack(pady=5)

        password_label = ttk.Label(self.register_frame, text="Senha:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        password_label.pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.register_frame, show="*", width=30, style='Dark.TEntry')
        self.reg_password_entry.pack(pady=5)

        interests_label = ttk.Label(self.register_frame, text="Principal Interesse:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        interests_label.pack(pady=5)
        self.interests_dropdown = ttk.Combobox(self.register_frame, textvariable=self.selected_interest,
                                                 values=self.user_interests_options, state="readonly", width=27)
        self.interests_dropdown.pack(pady=5)
        self.interests_dropdown.bind("<<ComboboxSelected>>", self._update_conditional_dropdowns)

        self.book_genre_label = ttk.Label(self.register_frame, text="Gênero de Livro:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.book_genre_dropdown = ttk.Combobox(self.register_frame, textvariable=self.selected_book_genre,
                                                 values=self.book_genres_options, state="readonly", width=27)

        self.tennis_type_label = ttk.Label(self.register_frame, text="Tipo de Tênis:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.tennis_type_dropdown = ttk.Combobox(self.register_frame, textvariable=self.selected_tennis_type,
                                                 values=self.tennis_type_options, state="readonly", width=27)

        self.home_appliance_type_label = ttk.Label(self.register_frame, text="Tipo de Eletrodoméstico:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.home_appliance_type_dropdown = ttk.Combobox(self.register_frame, textvariable=self.selected_home_appliance_type,
                                                          values=self.home_appliances_options, state="readonly", width=27)

        self.smartphone_brand_label = ttk.Label(self.register_frame, text="Marca de Smartphone:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.smartphone_brand_dropdown = ttk.Combobox(self.register_frame, textvariable=self.selected_smartphone_brand,
                                                          values=self.smartphone_brand_options, state="readonly", width=27)
        self._update_conditional_dropdowns()

        ttk.Button(self.register_frame, text="Registrar", command=self.register_user, style='Dark.TButton').pack(pady=10)
        ttk.Button(self.register_frame, text="Voltar para Login", command=self.create_login_frame, style='Dark.TButton').pack(pady=5)

    def _update_conditional_dropdowns(self, event=None):
        current_interest = self.selected_interest.get()

        if current_interest == "Livros":
            self.book_genre_label.pack(pady=5)
            self.book_genre_dropdown.pack(pady=5)
        else:
            self.book_genre_label.pack_forget()
            self.book_genre_dropdown.pack_forget()
            self.selected_book_genre.set(self.book_genres_options[0])

        if current_interest == "Tênis":
            self.tennis_type_label.pack(pady=5)
            self.tennis_type_dropdown.pack(pady=5)
        else:
            self.tennis_type_label.pack_forget()
            self.tennis_type_dropdown.pack_forget()
            self.selected_tennis_type.set(self.tennis_type_options[0])

        if current_interest == "Eletrodomésticos":
            self.home_appliance_type_label.pack(pady=5)
            self.home_appliance_type_dropdown.pack(pady=5)
        else:
            self.home_appliance_type_label.pack_forget()
            self.home_appliance_type_dropdown.pack_forget()
            self.selected_home_appliance_type.set(self.home_appliances_options[0])

        if current_interest == "Smartphones":
            self.smartphone_brand_label.pack(pady=5)
            self.smartphone_brand_dropdown.pack(pady=5)
        else:
            self.smartphone_brand_label.pack_forget()
            self.smartphone_brand_dropdown.pack_forget()
            self.selected_smartphone_brand.set(self.smartphone_brand_options[0]) 

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.db_manager.get_user_by_name(username)

        if user:
       
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                self.current_user = user
                messagebox.showinfo("Login", f"Bem-vindo, {self.current_user.name}!")
                self.create_main_app_frame()
            else:
                messagebox.showerror("Login", "Usuário ou senha inválidos.")
        else:
            messagebox.showerror("Login", "Usuário ou senha inválidos.")

    def register_user(self):
        username = self.reg_username_entry.get()
        contact_info = self.reg_contact_entry.get()
        password = self.reg_password_entry.get()
        selected_interest = self.selected_interest.get()

        selected_book_genre = self.selected_book_genre.get() if selected_interest == "Livros" else None
        selected_tennis_type = self.selected_tennis_type.get() if selected_interest == "Tênis" else None
        selected_home_appliance_type = self.selected_home_appliance_type.get() if selected_interest == "Eletrodomésticos" else None
        selected_smartphone_brand = self.selected_smartphone_brand.get() if selected_interest == "Smartphones" else None

        if not username or not contact_info or not password:
            messagebox.showerror("Cadastro", "Todos os campos são obrigatórios.")
            return

        if not self.validate_contact_info(contact_info):
            messagebox.showerror("Cadastro", "Formato de contato inválido. Use um e-mail válido ou um número de telefone.")
            return

        if self.db_manager.get_user_by_name(username):
            messagebox.showerror("Cadastro", "Nome de usuário já existe.")
            return

    
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user_interests = [selected_interest]
        if selected_interest == "Livros" and selected_book_genre:
            user_interests.append(selected_book_genre)

        if selected_interest == "Tênis" and selected_tennis_type:
            user_interests.append(selected_tennis_type)

        if selected_interest == "Eletrodomésticos" and selected_home_appliance_type:
            user_interests.append(selected_home_appliance_type)

        if selected_interest == "Smartphones" and selected_smartphone_brand:
            user_interests.append(selected_smartphone_brand)

        user_data = {
            'user_id': str(uuid.uuid4()),
            'name': username,
            'email': contact_info,
            'password_hash': hashed_password,
            'interests': user_interests
        }
        try:
            new_user = self.db_manager.add_user(user_data)
            if new_user:
                messagebox.showinfo("Cadastro", "Usuário registrado com sucesso! Faça login.")
                self.create_login_frame()
            else:
                messagebox.showerror("Cadastro", "Erro ao registrar usuário. Tente novamente.")
        except Exception as e:
            messagebox.showerror("Erro de Registro", f"Ocorreu um erro: {e}")
            print(f"Erro detalhado no registro: {e}")

    def validate_contact_info(self, contact_info):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.fullmatch(email_regex, contact_info):
            return True

        phone_regex = r'^\+?\d{8,15}$'
        if re.fullmatch(phone_regex, contact_info.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")):
            return True

        return False

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_main_app_frame(self):
        self.clear_frame()
        self.main_frame = ttk.Frame(self.master, padding="10", style='Dark.TFrame')
        self.main_frame.pack(expand=True, fill='both')

        navbar_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        navbar_frame.pack(fill='x', pady=5)

        ttk.Label(navbar_frame, text=f"Bem-vindo, {self.current_user.name}", background=self.secondary_color, foreground=self.text_color, font=self.font_header).pack(side='left', padx=10)
        ttk.Button(navbar_frame, text="Recomendações", command=self.show_recommendations, style='Dark.TButton').pack(side='left', padx=10)
        ttk.Button(navbar_frame, text="Histórico Recente", command=self.show_recent_views, style='Dark.TButton').pack(side='left', padx=10)
       
        ttk.Button(navbar_frame, text="Gerenciar Interesses", command=self.create_manage_interests_frame, style='Dark.TButton').pack(side='left', padx=10)
        ttk.Button(navbar_frame, text="Sair", command=self.logout, style='Dark.TButton').pack(side='right', padx=10)


        self.content_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.content_frame.pack(expand=True, fill='both', pady=10)

        self.show_recommendations()

    def create_manage_interests_frame(self):
    
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="Gerenciar Seus Interesses", style='Dark.TLabel', font=self.font_header).pack(pady=10)

        if self.current_user and self.current_user.interests:
            main_interest = self.current_user.interests[0] if self.current_user.interests else self.user_interests_options[0]
            if main_interest in self.user_interests_options:
                self.selected_new_interest.set(main_interest)
            else: 
                self.selected_new_interest.set(self.user_interests_options[0])
        else:
            self.selected_new_interest.set(self.user_interests_options[0])

        interests_label = ttk.Label(self.content_frame, text="Seu Principal Interesse Atual:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        interests_label.pack(pady=5)
        self.new_interests_dropdown = ttk.Combobox(self.content_frame, textvariable=self.selected_new_interest,
                                                 values=self.user_interests_options, state="readonly", width=27)
        self.new_interests_dropdown.pack(pady=5)
        self.new_interests_dropdown.bind("<<ComboboxSelected>>", self._update_new_conditional_dropdowns)

      
        self.new_book_genre_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
        self.new_tennis_type_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
        self.new_home_appliance_type_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
        self.new_smartphone_brand_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')

        self.new_book_genre_label = ttk.Label(self.new_book_genre_frame, text="Gênero de Livro:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.new_book_genre_dropdown = ttk.Combobox(self.new_book_genre_frame, textvariable=self.new_book_genre,
                                                 values=self.book_genres_options, state="readonly", width=27)

        self.new_tennis_type_label = ttk.Label(self.new_tennis_type_frame, text="Tipo de Tênis:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.new_tennis_type_dropdown = ttk.Combobox(self.new_tennis_type_frame, textvariable=self.new_tennis_type,
                                                 values=self.tennis_type_options, state="readonly", width=27)

        self.new_home_appliance_type_label = ttk.Label(self.new_home_appliance_type_frame, text="Tipo de Eletrodoméstico:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.new_home_appliance_type_dropdown = ttk.Combobox(self.new_home_appliance_type_frame, textvariable=self.new_home_appliance_type,
                                                          values=self.home_appliances_options, state="readonly", width=27)

        self.new_smartphone_brand_label = ttk.Label(self.new_smartphone_brand_frame, text="Marca de Smartphone:", background=self.secondary_color, foreground=self.text_color, font=self.font_body)
        self.new_smartphone_brand_dropdown = ttk.Combobox(self.new_smartphone_brand_frame, textvariable=self.new_smartphone_brand,
                                                          values=self.smartphone_brand_options, state="readonly", width=27)

        self._update_new_conditional_dropdowns()

        ttk.Button(self.content_frame, text="Salvar Interesses", command=self.save_interests, style='Dark.TButton').pack(pady=10)
        ttk.Button(self.content_frame, text="Voltar para Recomendações", command=self.show_recommendations, style='Dark.TButton').pack(pady=5)

    def _update_new_conditional_dropdowns(self, event=None):
       
        current_interest = self.selected_new_interest.get()

        self.new_book_genre.set(self.book_genres_options[0])
        self.new_tennis_type.set(self.tennis_type_options[0])
        self.new_home_appliance_type.set(self.home_appliances_options[0])
        self.new_smartphone_brand.set(self.smartphone_brand_options[0])

        self.new_book_genre_frame.pack_forget()
        self.new_tennis_type_frame.pack_forget()
        self.new_home_appliance_type_frame.pack_forget()
        self.new_smartphone_brand_frame.pack_forget()

        if current_interest == "Livros":
            self.new_book_genre_frame.pack(pady=5)
            self.new_book_genre_label.pack(side='left', padx=5)
            self.new_book_genre_dropdown.pack(side='left', padx=5)
        elif current_interest == "Tênis":
            self.new_tennis_type_frame.pack(pady=5)
            self.new_tennis_type_label.pack(side='left', padx=5)
            self.new_tennis_type_dropdown.pack(side='left', padx=5)
        elif current_interest == "Eletrodomésticos":
            self.new_home_appliance_type_frame.pack(pady=5)
            self.new_home_appliance_type_label.pack(side='left', padx=5)
            self.new_home_appliance_type_dropdown.pack(side='left', padx=5)
        elif current_interest == "Smartphones":
            self.new_smartphone_brand_frame.pack(pady=5)
            self.new_smartphone_brand_label.pack(side='left', padx=5)
            self.new_smartphone_brand_dropdown.pack(side='left', padx=5)

    def save_interests(self):

        if not self.current_user:
            messagebox.showerror("Erro", "Nenhum usuário logado.")
            return

        selected_interest = self.selected_new_interest.get()
        new_interests_list = [selected_interest]

        if selected_interest == "Livros":
            new_interests_list.append(self.new_book_genre.get())
        elif selected_interest == "Tênis":
            new_interests_list.append(self.new_tennis_type.get())
        elif selected_interest == "Eletrodomésticos":
            new_interests_list.append(self.new_home_appliance_type.get())
        elif selected_interest == "Smartphones":
            new_interests_list.append(self.new_smartphone_brand.get())

        try:
          
            success = self.db_manager.update_user_interests(self.current_user.user_id, new_interests_list)
            if success:
     
                self.current_user.interests = new_interests_list
                messagebox.showinfo("Sucesso", "Seus interesses foram atualizados!")
                self.show_recommendations() 
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar seus interesses.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar os interesses: {e}")

    def logout(self):
        self.current_user = None
        self.recent_views = LinkedList() 
        messagebox.showinfo("Sair", "Você foi desconectado.")
        self.create_login_frame()

    def open_product_link(self, product_link):

        print(f"DEBUG_OPEN_LINK: Função open_product_link chamada com link: '{product_link}'")
        if product_link:
            try:
                webbrowser.open_new(product_link)
                print(f"DEBUG_OPEN_LINK: Tentando abrir link: '{product_link}'")
            except Exception as e:
                print(f"DEBUG_OPEN_LINK: Erro ao abrir link '{product_link}': {e}")
                messagebox.showerror("Erro ao Abrir Link", f"Não foi possível abrir o link: {e}")
        else:
            print("DEBUG_OPEN_LINK: Link vazio ou None passado para open_product_link.")
            messagebox.showinfo("Link Indisponível", "Este produto não possui um link de compra disponível.")

    def show_recommendations(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="Recomendações Personalizadas", style='Dark.TLabel', font=self.font_header).pack(pady=10)

        content_recommender = self.recommendation_manager.content_based_recommender

        if content_recommender.products_df is None or content_recommender.tfidf_matrix is None:
            content_recommender._prepare_data()

        if content_recommender.products_df.empty:
            ttk.Label(self.content_frame, text="Não há produtos suficientes para gerar recomendações.", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(pady=20)
            return

        if self.current_user:
            recommended_products = self.recommendation_manager.get_user_recommendations(
                user_id=self.current_user.user_id,
                algorithm_type="content_based",
                num_recommendations=5
            )
        else:
            recommended_products = []
            print("Nenhum usuário logado para gerar recomendações personalizadas. Mostrando produtos genéricos.")

        if recommended_products:
            for i, product in enumerate(recommended_products):
                product_frame = ttk.Frame(self.content_frame, style='Dark.TFrame', borderwidth=1, relief="solid", padding=5)
                product_frame.pack(fill='x', padx=20, pady=5)
                ttk.Label(product_frame, text=f"Produto: {product.name}", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')
                ttk.Label(product_frame, text=f"Categoria: {product.category if product.category else 'N/A'}", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')
                ttk.Label(product_frame, text=f"Preço médio: R${product.price:.2f}" if product.price else "Preço médio: N/A", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')
                ttk.Label(product_frame, text=f"Descrição: {product.description[:100]}..." if product.description else "Descrição: N/A", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')

                interaction_frame = ttk.Frame(product_frame, style='Dark.TFrame')
                interaction_frame.pack(fill='x', pady=5)
                ttk.Button(interaction_frame, text="Ver Detalhes", command=lambda p=product: self.show_product_details(p), style='Dark.TButton').pack(side='left', padx=5)

                if product.link:
                    print(f"DEBUG_GUI: Criando botão 'Comprar Agora' para '{product.name}' com link: '{product.link}'")
                    ttk.Button(interaction_frame, text="Comprar Agora", command=lambda link=product.link: self.open_product_link(link), style='Dark.TButton').pack(side='left', padx=5)
                else:
                    print(f"DEBUG_GUI: Link indisponível para '{product.name}'. Exibindo texto 'Link indisponível'.")
                    ttk.Label(interaction_frame, text="Link indisponível", background=self.secondary_color, foreground=self.text_color, font=("Helvetica", 9, "italic")).pack(side='left', padx=5)

        else:
            ttk.Label(self.content_frame, text="Não foi possível gerar recomendações personalizadas no momento.", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(pady=20)

    def show_product_details(self, product):
        messagebox.showinfo("Detalhes do Produto",
                             f"ID: {product.product_id}\n"
                             f"Nome: {product.name}\n"
                             f"Descrição: {product.description}\n"
                             f"Preço médio: R${product.price:.2f}" if product.price else "Preço médio: N/A\n"
                             f"Categoria: {product.category if product.category else 'N/A'}\n"
                             f"Atributos: {product.attributes}\n"
                             f"Link: {product.link if product.link else 'N/A'}")

        if self.current_user:
      
            if self.recent_views.search(product.product_id):
                self.recent_views.delete(product.product_id)

            self.recent_views.prepend(product.product_id)

            while len(self.recent_views) > self.MAX_RECENT_VIEWS:
                last_item_data = self.recent_views.get_last_item()
                if last_item_data:
                    self.recent_views.delete(last_item_data)

    def show_recent_views(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="Seu Histórico de Visualizações Recentes", style='Dark.TLabel', font=self.font_header).pack(pady=10)

        if self.recent_views.is_empty():
            ttk.Label(self.content_frame, text="Nenhum produto visualizado recentemente nesta sessão.", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(pady=20)
            return

        recent_product_ids = self.recent_views.get_all()

        for product_id in recent_product_ids:
            product = self.db_manager.get_product_by_id(product_id)
            if product:
                product_frame = ttk.Frame(self.content_frame, style='Dark.TFrame', borderwidth=1, relief="solid", padding=5)
                product_frame.pack(fill='x', padx=20, pady=5)
                ttk.Label(product_frame, text=f"Produto: {product.name}", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')
                ttk.Label(product_frame, text=f"Categoria: {product.category if product.category else 'N/A'}", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')
                ttk.Label(product_frame, text=f"Preço médio: R${product.price:.2f}" if product.price else "Preço médio: N/A", background=self.secondary_color, foreground=self.text_color, font=self.font_body).pack(anchor='w')

                interaction_frame = ttk.Frame(product_frame, style='Dark.TFrame')
                interaction_frame.pack(fill='x', pady=5)
                ttk.Button(interaction_frame, text="Ver Detalhes", command=lambda p=product: self.show_product_details(p), style='Dark.TButton').pack(side='left', padx=5)
    
                if product.link:
                    ttk.Button(interaction_frame, text="Comprar Agora", command=lambda link=product.link: self.open_product_link(link), style='Dark.TButton').pack(side='left', padx=5)
                else:
                    ttk.Label(interaction_frame, text="Link indisponível", background=self.secondary_color, foreground=self.text_color, font=("Helvetica", 9, "italic")).pack(side='left', padx=5)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()