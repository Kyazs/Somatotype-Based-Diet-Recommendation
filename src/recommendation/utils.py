def handle_user_preferences(preferences):
    # Process user preferences for diet recommendations
    processed_preferences = {}
    # Example processing logic
    for key, value in preferences.items():
        processed_preferences[key] = value.lower()  # Normalize preferences
    return processed_preferences

def format_recommendations(recommendations):
    # Format the recommendations for output
    formatted_recommendations = []
    for item in recommendations:
        formatted_recommendations.append(f"- {item}")
    return "\n".join(formatted_recommendations)

def validate_preferences(preferences):
    # Validate user preferences to ensure they are acceptable
    valid_preferences = ['vegetarian', 'vegan', 'gluten-free', 'high-protein', 'low-carb']
    for preference in preferences:
        if preference not in valid_preferences:
            raise ValueError(f"Invalid preference: {preference}")
    return True