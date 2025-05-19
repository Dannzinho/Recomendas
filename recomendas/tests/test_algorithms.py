import unittest
import json
import pandas as pd
from src.algorithms.content_based import load_products, calculate_similarity, get_recommendations_content_based
from src.algorithms.collaborative import load_feedback, create_user_item_matrix, calculate_user_similarity, get_collaborative_recommendations

class TestContentBased(unittest.TestCase):

    def setUp(self):
        self.products_data = [
            {"product_id": "p1", "name": "Laptop A", "category": "electronics", "features": ["fast"]},
            {"product_id": "p2", "name": "Laptop B", "category": "electronics", "features": ["slow"]},
            {"product_id": "b1", "name": "Book X", "category": "books", "genre": ["fiction"]},
            {"product_id": "b2", "name": "Book Y", "category": "books", "genre": ["non-fiction"]},
        ]
        with open("src/data/test_products.json", 'w') as f:
            json.dump(self.products_data, f)
        self.products_df = load_products("src/data/test_products.json")
        self.cosine_sim = calculate_similarity(self.products_df.copy())

        self.users_data = [
            {"user_id": "u1", "purchase_history": ["p1"]},
            {"user_id": "u2", "purchase_history": ["b2"]},
        ]
        with open("src/data/test_users.json", 'w') as f:
            json.dump(self.users_data, f)
        with open("src/data/users.json", 'w') as f:
            json.dump(self.users_data, f)

    def tearDown(self):
        import os
        os.remove("src/data/test_products.json")
        os.remove("src/data/users.json") 

    def test_load_products(self):
        self.assertIsInstance(self.products_df, pd.DataFrame)
        self.assertEqual(len(self.products_df), 4)

    def test_calculate_similarity(self):
        self.assertEqual(self.cosine_sim.shape, (4, 4))
        self.assertAlmostEqual(self.cosine_sim[0, 0], 1.0)
        self.assertAlmostEqual(self.cosine_sim[1, 1], 1.0)
        self.assertAlmostEqual(self.cosine_sim[2, 2], 1.0)
        self.assertAlmostEqual(self.cosine_sim[3, 3], 1.0)

    def test_get_recommendations_content_based(self):

        recommendations_u1 = get_recommendations_content_based("u1", self.products_df, self.cosine_sim, self.users_data)
        self.assertIn("p2", recommendations_u1)
        self.assertNotIn("p1", recommendations_u1)
        recommendations_u2 = get_recommendations_content_based("u2", self.products_df, self.cosine_sim, self.users_data)
        self.assertIn("b1", recommendations_u2)
        self.assertNotIn("b2", recommendations_u2)

        users_no_history = [{"user_id": "u3", "purchase_history": []}]
        recommendations_u3 = get_recommendations_content_based("u3", self.products_df, self.cosine_sim, users_no_history)
        self.assertEqual(recommendations_u3, [])

class TestCollaborative(unittest.TestCase):

    def setUp(self):
        self.feedback_data = {
            "ratings": [
                {"user_id": "u1", "product_id": "p1", "rating": 5},
                {"user_id": "u1", "product_id": "p2", "rating": 4},
                {"user_id": "u2", "product_id": "p1", "rating": 3},
                {"user_id": "u2", "product_id": "p3", "rating": 5},
            ]
        }
        with open("src/data/test_feedback.json", 'w') as f:
            json.dump(self.feedback_data, f)
        self.feedback_df = load_feedback("src/data/test_feedback.json")

        self.users_data = [{"user_id": "u1"}, {"user_id": "u2"}]
        with open("src/data/test_users_collab.json", 'w') as f:
            json.dump(self.users_data, f)
        with open("src/data/users.json", 'w') as f:
            json.dump(self.users_data, f)
        self.users_df = load_users("src/data/test_users_collab.json")

    
        self.products_data = [{"product_id": "p1"}, {"product_id": "p2"}, {"product_id": "p3"}]
        with open("src/data/test_products_collab.json", 'w') as f:
            json.dump(self.products_data, f)
        with open("src/data/products.json", 'w') as f: 
            json.dump(self.products_data, f)
        self.products_df = load_products("src/data/test_products_collab.json")

    def tearDown(self):
        import os
        os.remove("src/data/test_feedback.json")
        os.remove("src/data/test_users_collab.json")
        os.remove("src/data/products.json") 

    def test_load_feedback(self):
        self.assertIsInstance(self.feedback_df, pd.DataFrame)
        self.assertEqual(len(self.feedback_df), 4)

    def test_create_user_item_matrix(self):
        matrix, users, products = create_user_item_matrix(self.feedback_df)
        self.assertIsInstance(matrix, pd.DataFrame)
        self.assertEqual(matrix.shape, (2, 3)) 
        self.assertEqual(users, ["u1", "u2"])
        self.assertEqual(products, ["p1", "p2", "p3"])
        self.assertEqual(matrix.loc["u1", "p1"], 5.0)
        self.assertEqual(matrix.loc["u2", "p2"], 0.0)

    def test_calculate_user_similarity(self):
        matrix, _, _ = create_user_item_matrix(self.feedback_df)
        similarity, users = calculate_user_similarity(matrix)
        self.assertIsInstance(similarity, pd.DataFrame)
        self.assertEqual(similarity.shape, (2, 2))
        self.assertEqual(list(users), ["u1", "u2"])
        self.assertAlmostEqual(similarity.loc["u1", "u1"], 1.0)
        self.assertAlmostEqual(similarity.loc["u2", "u2"], 1.0)

    def test_get_collaborative_recommendations(self):
        matrix, users, products = create_user_item_matrix(self.feedback_df)
        similarity, user_index = calculate_user_similarity(matrix)

        if users and "u1" in users and products:
            recommendations_u1 = get_collaborative_recommendations("u1", matrix, similarity.values, list(similarity.index), products)
            self.assertIn("p3", recommendations_u1)
            self.assertNotIn("p1", recommendations_u1) 
            self.assertNotIn("p2", recommendations_u1) 

        if users and "u2" in users and products:
            recommendations_u2 = get_collaborative_recommendations("u2", matrix, similarity.values, list(similarity.index), products)
            self.assertIn("p2", recommendations_u2)
            self.assertNotIn("p1", recommendations_u2)
            self.assertNotIn("p3", recommendations_u2) 

if __name__ == '__main__':
    unittest.main()