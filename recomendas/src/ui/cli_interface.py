import json
from src.algorithms.content_based import load_products, calculate_similarity, get_recommendations_content_based
from src.algorithms.collaborative import load_feedback, create_user_item_matrix, calculate_user_similarity, get_collaborative_recommendations, load_users
from src.utils.recommendation_manager import RecommendationHistoryManager
from src.utils.metrics import load_interactions, calculate_click_count, calculate_acceptance_rate, get_feedback_summary

def load_data():
    products_df = load_products()
    with open("src/data/users.json", 'r') as f:
        users_data = json.load(f)
    feedback_df = load_feedback()
    interactions = load_interactions()
    return products_df, users_data, feedback_df, interactions

def main_cli():
    print("\nBem-vindo ao Recomendas!")
    print("=========================")

    products_df, users_data, feedback_df, interactions = load_data()
    history_manager = RecommendationHistoryManager()

    cosine_sim = calculate_similarity(products_df.copy())
    user_item_matrix, user_ids, product_ids = create_user_item_matrix(feedback_df)
    user_similarity, _ = calculate_user_similarity(user_item_matrix)

    while True:
        user_id = input("Digite seu ID de usuário (ou 'sair' para encerrar, 'cadastrar' para novo usuário): ").strip()
        if user_id.lower() == 'sair':
            break
        elif user_id.lower() == 'cadastrar':
            name = input("Digite seu nome: ").strip()
            email = input("Digite seu e-mail: ").strip()
            new_user = {"user_id": email.split('@')[0], "name": name, "email": email, "purchase_history": []}
            users_data.append(new_user)
            with open("src/data/users.json", 'w') as f:
                json.dump(users_data, f, indent=2)
            print(f"Usuário '{new_user['name']}' cadastrado com ID '{new_user['user_id']}'.")
            continue

        user = next((u for u in users_data if u['user_id'] == user_id), None)
        if not user:
            print("Usuário não encontrado.")
            continue

        print(f"\nOpções para o usuário {user['name']} ({user_id}):")
        print("1. Obter recomendações baseadas em conteúdo")
        print("2. Obter recomendações colaborativas")
        print("3. Ver histórico de recomendações")
        print("4. Ver métricas")
        print("5. Sair")

        choice = input("Digite sua escolha: ").strip()

        if choice == '1':
            recommendations = get_recommendations_content_based(user_id, products_df, cosine_sim, users_data)
            if recommendations:
                print("\nRecomendações baseadas em conteúdo:")
                for rec_id in recommendations:
                    product = products_df[products_df['product_id'] == rec_id].iloc[0]
                    print(f"- {product['name']} ({rec_id})")
                    history_manager.add_recommendation(user_id, rec_id)
            else:
                print("Não há recomendações baseadas em conteúdo para você no momento.")

        elif choice == '2':
            if user_ids and user_id in user_ids:
                recommendations = get_collaborative_recommendations(user_id, user_item_matrix, user_similarity, user_ids, product_ids)
                if recommendations:
                    print("\nRecomendações colaborativas:")
                    for rec_id in recommendations:
                        product = products_df[products_df['product_id'] == rec_id].iloc[0]
                        print(f"- {product['name']} ({rec_id})")
                        history_manager.add_recommendation(user_id, rec_id)
                else:
                    print("Não há recomendações colaborativas para você no momento.")
            else:
                print("Não há dados suficientes para recomendações colaborativas para este usuário.")

        elif choice == '3':
            history_manager.display_history(user_id)

        elif choice == '4':
            print("\nMétricas:")
            user_interactions = [i for i in interactions if i.get('user_id') == user_id]
            print(f"  Seus feedbacks: {len([f for f in feedback_df.to_dict('records') if f.get('user_id') == user_id])}")
            print(f"  Seus clicks: {calculate_click_count(user_interactions)}")
            acceptance_count = len([i for i in user_interactions if i.get('type') == 'accept'])
            total_interactions = len(user_interactions)
            acceptance_rate = (acceptance_count / total_interactions) * 100 if total_interactions > 0 else 0
            print(f"  Sua taxa de aceitação (aproximada): {acceptance_rate:.2f}%")

        elif choice == '5':
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main_cli()