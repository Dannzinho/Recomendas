import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db_manager import DBManager, Product
from src.algorithms.content_based import ContentBasedRecommender

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.content_based_recommender = ContentBasedRecommender(db_manager)

    def get_user_recommendations(self, user_id, algorithm_type="content_based", num_recommendations=5):
        if algorithm_type == "content_based":
            if self.content_based_recommender:
                print(f"Gerando recomendações baseadas em conteúdo para o usuário: {user_id}")
                return self.content_based_recommender.get_recommendations_for_user_interests(user_id, num_recommendations)
            else:
                print("Erro: ContentBasedRecommender não inicializado.")
                return []
        else:
            print(f"Tipo de algoritmo de recomendação '{algorithm_type}' não suportado.")
            return self.get_popular_products(num_recommendations)

    def get_popular_products(self, num_products=5):
        session = self.db_manager.get_session()
        try:
            feedback_df = self.db_manager.load_data_into_df('feedback')
            if not feedback_df.empty:
                product_ratings = feedback_df.groupby('product_id')['rating'].mean()
                product_counts = feedback_df.groupby('product_id')['rating'].count()
                valid_products = product_counts[product_counts >= 2].index
                filtered_ratings = product_ratings[product_ratings.index.isin(valid_products)]
                top_product_ids = filtered_ratings.nlargest(num_products).index.tolist()
            else:
                logging.info("Não há feedbacks para determinar produtos populares. Retornando os últimos produtos adicionados.")
                top_product_ids = [p.product_id for p in session.query(Product).order_by(Product.id.desc()).limit(num_products).all()]

            recommended_products = []
            for p_id in top_product_ids:
                product_detail = self.db_manager.get_product_by_id(p_id)
                if product_detail:
                    recommended_products.append(product_detail.to_dict()) 
            return recommended_products
        except Exception as e:
            print(f"Erro ao obter produtos populares: {e}")
            return []
        finally:
            session.close()
