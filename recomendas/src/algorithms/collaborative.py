import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from src.database.db_manager import DBManager

db_manager = DBManager()

def load_feedback():
    return db_manager.load_data_into_df('feedback')

def load_users():
    return db_manager.load_data_into_df('users')

def load_products():
    return db_manager.load_data_into_df('products')

def create_user_item_matrix(feedback_df):
    if feedback_df.empty:
        return None, None, None
    user_item_matrix = feedback_df.pivot_table(index='user_id', columns='product_id', values='rating')
    user_ids = user_item_matrix.index.tolist()
    product_ids = user_item_matrix.columns.tolist()
    return user_item_matrix.fillna(0), user_ids, product_ids

def calculate_user_similarity(user_item_matrix):
    if user_item_matrix is None:
        return None, None
    user_similarity = cosine_similarity(user_item_matrix)
    return user_similarity, user_item_matrix.index

def get_collaborative_recommendations(user_id, user_item_matrix, user_similarity, user_ids, product_ids, top_n=5):
    if user_item_matrix is None or user_similarity is None or user_id not in user_ids:
        return []

    user_index = user_ids.index(user_id)
    similarity_scores = pd.Series(user_similarity[user_index], index=user_ids)
    similar_users = similarity_scores.sort_values(ascending=False).drop(user_id, errors='ignore')

    rated_products = user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index.tolist()

    recommendations = {}
    for similar_user_id, similarity in similar_users.items():
        if similar_user_id in user_item_matrix.index:
            similar_user_rated_products = user_item_matrix.loc[similar_user_id][user_item_matrix.loc[similar_user_id] > 0].index.tolist()
            unseen_products = [product for product in similar_user_rated_products if product not in rated_products]

            for product_id in unseen_products:
                if product_id not in recommendations:
                    recommendations[product_id] = 0
                if product_id in user_item_matrix.columns:
                    recommendations[product_id] += similarity * user_item_matrix.loc[similar_user_id, product_id]

    sorted_recommendations = sorted(recommendations.items(), key=lambda item: item[1], reverse=True)
    return [product_id for product_id, score in sorted_recommendations[:top_n]]

if __name__ == '__main__':
    feedback_df = load_feedback()
    users_df = load_users()
    products_df = load_products()

    user_item_matrix, user_ids, product_ids = create_user_item_matrix(feedback_df)
    user_similarity, user_index_list = calculate_user_similarity(user_item_matrix)

    if user_ids:
        user_id_to_recommend = user_ids[0]
        if product_ids is None:
            print("Não há dados de feedback para criar a matriz user-item.")
        else:
            recommendations = get_collaborative_recommendations(user_id_to_recommend, user_item_matrix, user_similarity, user_ids, product_ids)
            print(f"Recomendações colaborativas para o usuário {user_id_to_recommend}: {recommendations}")
    else:
        print("Não há dados de feedback para gerar recomendações colaborativas.")
