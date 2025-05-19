import json
from collections import defaultdict

def load_interactions(file_path="src/data/feedback.json"):
    with open(file_path, 'r') as f:
        feedback_data = json.load(f)
    return feedback_data.get('interactions', [])

def calculate_click_count(interactions, user_id=None):
    count = 0
    for interaction in interactions:
        if interaction.get('type') == 'click':
            if user_id and interaction.get('user_id') == user_id:
                count += 1
            elif user_id is None:
                count += 1
    return count

def calculate_acceptance_rate(interactions, user_id=None):
    acceptance_count = 0
    total_interactions = 0
    for interaction in interactions:
        if user_id and interaction.get('user_id') == user_id:
            total_interactions += 1
            if interaction.get('type') == 'accept':
                acceptance_count += 1
        elif user_id is None:
            total_interactions += 1
            if interaction.get('type') == 'accept':
                acceptance_count += 1

    return (acceptance_count / total_interactions) * 100 if total_interactions > 0 else 0

def get_feedback_summary(interactions, user_id=None, feedback_type='rating'):
    feedback_values = []
    for interaction in interactions:
        if interaction.get('type') == feedback_type:
            if user_id and interaction.get('user_id') == user_id:
                rating = interaction.get(feedback_type)
                if rating is not None:
                    feedback_values.append(rating)
            elif user_id is None:
                rating = interaction.get(feedback_type)
                if rating is not None:
                    feedback_values.append(rating)

    if feedback_values:
        return sum(feedback_values) / len(feedback_values)
    return 0

if __name__ == '__main__':
    interactions = load_interactions()

    total_clicks = calculate_click_count(interactions)
    print(f"Total de cliques: {total_clicks}")

    user1_clicks = calculate_click_count(interactions, user_id="daniel")
    print(f"Cliques do usuário daniel: {user1_clicks}")

    total_accepts = calculate_acceptance_rate(interactions)
    print(f"Total de aceitações: {total_accepts:.2f}%")

    user1_avg_rating = get_feedback_summary(interactions, user_id="daniel", feedback_type='rating')
    print(f"Avaliação média do usuário daniel: {user1_avg_rating:.2f}")