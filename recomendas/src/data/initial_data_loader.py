# src/data/initial_data_loader.py

import json
import os
import uuid
from datetime import datetime
import logging

from src.database.db_manager import DBManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_initial_data(db_manager):
    logging.info("Iniciando carga de dados iniciais...")

    try:
        db_manager.clear_all_tables()
        db_manager.create_tables()
        logging.info("Tabelas limpas e recriadas com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao limpar e recriar tabelas: {e}")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Carregar categorias
    categories_file = os.path.join(current_dir, 'categories.json')
    if os.path.exists(categories_file):
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)

            def process_category_entry(category_dict, parent_id=None, level="primary"):
                category_id = category_dict['id']
                category_name = category_dict['name']
                category_type = f"{level}_product_category"

                try:
                    db_manager.add_category({
                        "id": category_id,
                        "name": category_name,
                        "type": category_type
                    })
                except Exception as e:
                    logging.error(f"Erro ao adicionar categoria '{category_name}': {e}")

                if 'subcategories' in category_dict:
                    for sub_cat in category_dict['subcategories']:
                        process_category_entry(sub_cat, parent_id=category_id, level="sub")

                if 'items' in category_dict:
                    for item in category_dict['items']:
                        try:
                            db_manager.add_category({
                                "id": item['id'],
                                "name": item['name'],
                                "type": "item_product_category"
                            })
                        except Exception as e:
                            logging.error(f"Erro ao adicionar item/categoria '{item['name']}': {e}")

            for top_level_category in categories_data:
                process_category_entry(top_level_category)

            logging.info(f"Categorias carregadas de '{categories_file}'.")
    else:
        logging.warning(f"Arquivo '{categories_file}' não encontrado.")

    # Carregar produtos
    products_file = os.path.join(current_dir, 'products.json')
    if os.path.exists(products_file):
        with open(products_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            for product_entry in products_data:
                if 'product_id' not in product_entry or not product_entry['product_id']:
                    product_entry['product_id'] = str(uuid.uuid4())
                db_manager.add_product(product_entry)
        logging.info(f"Produtos carregados de '{products_file}'.")
    else:
        logging.error(f"Arquivo '{products_file}' não encontrado.")
        return

    # Carregar usuários
    users_file = os.path.join(current_dir, 'users.json')
    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            for user_entry in users_data:
                if 'user_id' not in user_entry:
                    user_entry['user_id'] = str(uuid.uuid4())
                db_manager.add_user(user_entry)
        logging.info(f"Usuários carregados de '{users_file}'.")
    else:
        logging.warning(f"Arquivo '{users_file}' não encontrado.")

    # Carregar interações
    interactions_file = os.path.join(current_dir, 'interactions.json')
    if os.path.exists(interactions_file):
        with open(interactions_file, 'r', encoding='utf-8') as f:
            interactions_data = json.load(f)
            for entry in interactions_data:
                if isinstance(entry.get('timestamp'), str):
                    try:
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                    except ValueError:
                        logging.warning(f"Data inválida em interação '{entry.get('id')}', usando data atual.")
                        entry['timestamp'] = datetime.now()
                db_manager.add_interaction(entry)
        logging.info(f"Interações carregadas de '{interactions_file}'.")
    else:
        logging.warning(f"Arquivo '{interactions_file}' não encontrado.")

    # Carregar feedbacks
    feedbacks_file = os.path.join(current_dir, 'feedback.json')
    if os.path.exists(feedbacks_file):
        with open(feedbacks_file, 'r', encoding='utf-8') as f:
            feedbacks_data = json.load(f)
            for entry in feedbacks_data:
                if isinstance(entry.get('timestamp'), str):
                    try:
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                    except ValueError:
                        logging.warning(f"Data inválida em feedback '{entry.get('id')}', usando data atual.")
                        entry['timestamp'] = datetime.now()
                db_manager.add_feedback(entry)
        logging.info(f"Feedbacks carregados de '{feedbacks_file}'.")
    else:
        logging.warning(f"Arquivo '{feedbacks_file}' não encontrado.")

    logging.info("Carga de dados concluída com sucesso.")

if __name__ == '__main__':
    db_manager = DBManager()
    load_initial_data(db_manager)
