from src.structures.linked_list import LinkedList

class RecommendationHistoryManager:
    def __init__(self, max_history_size=5):
        self.user_histories = {}
        self.max_history_size = max_history_size

    def add_recommendation(self, user_id, product_id):
        if user_id not in self.user_histories:
            self.user_histories[user_id] = LinkedList()

        history = self.user_histories[user_id]
        history.append(product_id)

        while len(history) > self.max_history_size:
            if history.head:
                history.delete(history.head.data)

    def get_history(self, user_id):
        if user_id in self.user_histories:
            return self.user_histories[user_id].get_all()
        return []

    def display_history(self, user_id):
        if user_id in self.user_histories:
            print(f"Histórico de recomendações para o usuário {user_id}: {self.user_histories[user_id]}")
        else:
            print(f"Nenhum histórico de recomendações encontrado para o usuário {user_id}.")

if __name__ == '__main__':
    history_manager = RecommendationHistoryManager(max_history_size=3)

    history_manager.add_recommendation("user1", "productA")
    history_manager.add_recommendation("user1", "productB")
    history_manager.add_recommendation("user1", "productC")
    history_manager.add_recommendation("user1", "productD")

    history_manager.display_history("user1")
    print(f"Histórico de user1 (lista): {history_manager.get_history('user1')}")

    history_manager.add_recommendation("user2", "productX")
    history_manager.display_history("user2")