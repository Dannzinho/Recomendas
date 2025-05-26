from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import logging

from src.database.db_manager import DBManager, Product, User

portuguese_stop_words = [
    'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'às', 'até', 'com', 'como', 'da', 'das',
    'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do', 'dos', 'e', 'é', 'ela', 'elas', 'ele', 'eles', 'em', 'entre',
    'era', 'eram', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes', 'eu', 'foi', 'fomos', 'for',
    'foram', 'fosse', 'fossem', 'fui', 'há', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu',
    'meus', 'minha', 'minhas', 'muito', 'na', 'nas', 'nem', 'no', 'nos', 'nossa', 'nossas', 'nosso', 'nossos', 'num',
    'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'se',
    'sem', 'ser', 'será', 'serão', 'seria', 'seriam', 'seu', 'seus', 'só', 'somos', 'sua', 'suas', 'também', 'te',
    'tem', 'têm', 'temos', 'tenho', 'ter', 'terá', 'terão', 'teria', 'teriam', 'teu', 'teus', 'ti', 'tinha', 'tinham',
    'tínhamos', 'tive', 'tivera', 'tiveram', 'tivesse', 'tivessem', 'tu', 'tua', 'tuas', 'um', 'uma', 'uns', 'você', 'vocês',
    'vos', 'esteja', 'estejam', 'estejamos', 'estava', 'estávamos', 'esteve', 'estive', 'estivemos', 'estivera',
    'estiverem', 'estivermos', 'estivessem', 'estivessemos', 'estou', 'fôramos', 'fôssemos', 'haja', 'hajam', 'hajamos',
    'havei', 'havemos', 'haver', 'haverá', 'haverão', 'haverei', 'haveremos', 'haveria', 'haveriam', 'houvera',
    'houvéramos', 'houver', 'houverá', 'houverão', 'houverei', 'houveremos', 'houveria', 'houveriam', 'houvesse',
    'houvéssemos', 'ia', 'íamos', 'iam', 'ida', 'idas', 'ido', 'idos', 'indo', 'ir', 'irei', 'iremos', 'iria', 'iriam',
    'lugar', 'mim', 'mundo', 'naquele', 'naquela', 'naqueles', 'naquelas', 'nas', 'nem', 'pode', 'podia', 'podeis',
    'podem', 'podemos', 'poder', 'poderá', 'poderão', 'poderei', 'poderemos', 'poderia', 'poderiam', 'podias', 'porém',
    'pra', 'quais', 'quanto', 'quantos', 'quantas', 'quer', 'queira', 'queiram', 'queremos', 'quero', 'quis', 'quise',
    'quiseram', 'quiserem', 'quiséssemos', 'sempre', 'serei', 'seremos', 'si', 'sido', 'sou', 'talvez', 'tende',
    'tenha', 'tenham', 'tenhamos', 'terei', 'teremos', 'vendo', 'vir', 'virá', 'virão', 'virei', 'viremos', 'viria',
    'viriam', 'viu', 'tudo', 'umas', 'vai', 'vamos', 'ir'
]

class ContentBasedRecommender:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.products_df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self._prepare_data()

    def _prepare_data(self):
        try:
            products_from_db = self.db_manager.get_all_products()
            if not products_from_db:
                self.products_df = pd.DataFrame()
                self.tfidf_matrix = None
                return

            self.products_df = pd.DataFrame([p.to_dict() for p in products_from_db])
            self.products_df['content'] = self.products_df['name'].fillna('') + ' ' + \
                                          self.products_df['category'].fillna('') + ' ' + \
                                          self.products_df['brand'].fillna('') + ' ' + \
                                          self.products_df['description'].fillna('')

            def extract_attributes_for_content(row):
                attrs_text = []
                if isinstance(row['attributes'], dict):
                    for value in row['attributes'].values():
                        if isinstance(value, list):
                            attrs_text.extend([str(item) for item in value])
                        else:
                            attrs_text.append(str(value))
                return ' '.join(attrs_text)

            self.products_df['attributes_text'] = self.products_df.apply(extract_attributes_for_content, axis=1)
            self.products_df['content'] = self.products_df['content'] + ' ' + self.products_df['attributes_text'].fillna('')
            self.products_df['content'] = self.products_df['content'].apply(lambda x: x.lower())
            self.products_df['category'] = self.products_df['category'].apply(lambda x: x.lower() if x else '')
            self.products_df['tipo_tenis'] = self.products_df['attributes'].apply(
                lambda x: x.get('tipo_tenis').lower() if isinstance(x, dict) and x.get('tipo_tenis') else None
            )

            self.tfidf_vectorizer = TfidfVectorizer(stop_words=portuguese_stop_words)
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.products_df['content'])

        except Exception as e:
            logging.error(f"Erro ao preparar dados para recomendação: {e}")
            self.products_df = pd.DataFrame()
            self.tfidf_matrix = None

    def get_recommendations_for_user_interests(self, user_id, num_recommendations=5):
        user = self.db_manager.get_user_by_id(user_id)
        if not user or not user.interests:
            return self.db_manager.get_all_products()[:num_recommendations]

        user_interests = [interest.lower() for interest in user.interests]
        is_tennis_interest = "tênis" in user_interests
        tennis_type_filter = "casual" if "casual" in user_interests else "esportivo" if "esportivo" in user_interests else None
        user_profile_text = " ".join(user_interests)

        if not user_profile_text.strip() or self.tfidf_vectorizer is None:
            return []

        user_tfidf = self.tfidf_vectorizer.transform([user_profile_text])
        filtered_products_df = self.products_df.copy()

        if is_tennis_interest:
            filtered_products_df = filtered_products_df[filtered_products_df['category'] == 'tênis']
            if tennis_type_filter:
                filtered_products_df = filtered_products_df[filtered_products_df['tipo_tenis'] == tennis_type_filter]

        if filtered_products_df.empty or self.tfidf_matrix is None:
            return self.db_manager.get_all_products()[:num_recommendations]

        original_indices = filtered_products_df.index
        tfidf_matrix_filtered = self.tfidf_matrix[original_indices]
        cosine_similarities = linear_kernel(user_tfidf, tfidf_matrix_filtered).flatten()

        num_to_select = min(num_recommendations, len(cosine_similarities))
        if num_to_select == 0:
            return []

        top_indices = cosine_similarities.argsort()[-num_to_select:][::-1]
        recommended_ids = filtered_products_df.iloc[top_indices]['product_id'].tolist()
        recommended_products = [self.db_manager.get_product_by_id(pid) for pid in recommended_ids]

        return [p for p in recommended_products if p is not None]
