class Recommender:
    def __init__(self, user_preferences, cnn_outputs):
        self.user_preferences = user_preferences
        self.cnn_outputs = cnn_outputs

    def generate_recommendations(self):
        recommendations = []
        # Logic to generate diet recommendations based on user preferences and CNN outputs
        # This is a placeholder for the actual recommendation logic
        if self.cnn_outputs['somatotype'] == 'ectomorph':
            recommendations.append('High-calorie diet with protein-rich foods')
        elif self.cnn_outputs['somatotype'] == 'mesomorph':
            recommendations.append('Balanced diet with a mix of protein, carbs, and fats')
        elif self.cnn_outputs['somatotype'] == 'endomorph':
            recommendations.append('Low-carb diet with high protein intake')

        # Further refine recommendations based on user preferences
        recommendations = self.refine_recommendations(recommendations)
        return recommendations

    def refine_recommendations(self, recommendations):
        refined_recommendations = []
        for recommendation in recommendations:
            if 'vegetarian' in self.user_preferences and 'meat' in recommendation:
                continue
            refined_recommendations.append(recommendation)
        return refined_recommendations

    def display_recommendations(self):
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            print(f'Recommendation: {rec}')