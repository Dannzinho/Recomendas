import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

def load_products(file_path="src/data/products.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        return pd.DataFrame(products)
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {file_path}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON em {file_path}: {e}")
        return pd.DataFrame()

def get_product_features(product):
    features = []
    if 'category' in product:
        features.append(str(product['category']))
    if 'brand' in product:
        features.append(str(product['brand']))
    if 'features' in product and isinstance(product['features'], list):
        features.extend(map(str, product['features']))
    if 'style' in product:
        features.append(str(product['style']))
    if 'genre' in product:
        features.append(str(product['genre']))
    if 'material' in product:
        features.append(str(product['material']))
    return ' '.join(filter(None, features))

def calculate_similarity(products_df):
    products_df['features_text'] = products_df.apply(get_product_features, axis=1)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(products_df['features_text'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def get_recommendations_content_based(user_id, products_df, cosine_sim, users_data, top_n=5):
    user = next((user for user in users_data if user['user_id'] == user_id), None)
    if not user or not user.get('purchase_history'):
        return []

    purchased_products = products_df[products_df['product_id'].isin(user['purchase_history'])]

    if purchased_products.empty:
        return []

    purchased_indices = purchased_products.index

    similarity_scores = pd.Series(0.0, index=products_df.index)
    for index in purchased_indices:
        similarity_scores += cosine_sim[index]

    similarity_scores = similarity_scores.drop(purchased_indices, errors='ignore')

    top_indices = similarity_scores.nlargest(top_n).index
    recommendations = products_df.loc[top_indices]['product_id'].tolist()

    return recommendations

if __name__ == '__main__':
    products_df = load_products()
    cosine_sim = calculate_similarity(products_df.copy())

    with open("src/data/users.json", 'r') as f:
        users_data = json.load(f)

    user_id_to_recommend = "daniel"
    recommendations = get_recommendations_content_based(user_id_to_recommend, products_df, cosine_sim, users_data)
    print(f"Recomendações baseadas em conteúdo para o usuário {user_id_to_recommend}: {recommendations}")