import csv
import pandas as pd
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR  # Correct import path
# -----------------------------
# Synthetic diet dataset (CSV)
# -----------------------------

with open("diet_templates.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["somatotype", "goal", "protein_g", "carbs_g", "fats_g", "foods"],
    )
    writer.writeheader()
    writer.writerows(
        [
            {
                "somatotype": "ectomorph",
                "goal": "weight_gain",
                "protein_g": 150,
                "carbs_g": 300,
                "fats_g": 80,
                "foods": "Oats, Peanut Butter, Grilled Chicken, Rice, Protein Shake, Salmon, Sweet Potatoes",
            },
            {
                "somatotype": "ectomorph",
                "goal": "weight_loss",
                "protein_g": 130,
                "carbs_g": 180,
                "fats_g": 60,
                "foods": "Boiled Eggs, Tuna, Salad Greens, Quinoa, Vegetables, Cottage Cheese",
            },
            {
                "somatotype": "mesomorph",
                "goal": "weight_gain",
                "protein_g": 140,
                "carbs_g": 250,
                "fats_g": 70,
                "foods": "Greek Yogurt, Chicken Breast, Pasta, Turkey, Whole Grain Bread, Beef, Brown Rice",
            },
            {
                "somatotype": "mesomorph",
                "goal": "weight_loss",
                "protein_g": 130,
                "carbs_g": 180,
                "fats_g": 60,
                "foods": "Omelette, Grilled Fish, Salad, Lentils, Tofu, Broccoli",
            },
            {
                "somatotype": "endomorph",
                "goal": "weight_gain",
                "protein_g": 140,
                "carbs_g": 200,
                "fats_g": 80,
                "foods": "Scrambled Eggs, Avocado, Chicken Thighs, Broccoli, Greek Yogurt, Nuts, Tuna",
            },
            {
                "somatotype": "endomorph",
                "goal": "weight_loss",
                "protein_g": 150,
                "carbs_g": 120,
                "fats_g": 50,
                "foods": "Boiled Chicken, Steamed Vegetables, Protein Smoothie, Grilled Tofu, Salad",
            },
        ]
    )

"""
-----------------------------------
Recommender System Implementation
-----------------------------------
The calculate_bmr function computes the Basal Metabolic Rate (BMR),
which is the number of calories required to keep your body functioning at rest.
Arguments:
- weight: Weight in kilograms (float or int)
- height: Height in centimeters (float or int)
- age: Age in years (int)
- sex: Biological sex ("male" or "female")
Returns:
- BMR value as a float
"""


def calculate_bmr(weight, height, age, sex):
    if sex == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161
    

"""
Calculates the activity multiplier based on the given activity level.
Args:
    level (str): The activity level, which can be one of the following:
    "sedentary", "light", "moderate", or "very_active". Defaults to 1.2 if the level is not recognized.

Returns:
    float: The activity multiplier corresponding to the given activity level.
"""

def get_activity_multiplier(level):

    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
    }.get(level, 1.2)


class Recommender:
    """
    A class to provide diet recommendations based on user data, somatotype, and fitness goals.
    Attributes:
        user_data (dict): A dictionary containing user-specific data such as weight, height, age, sex, and activity level.
        goal (str): The user's fitness goal (e.g., "weight_loss", "weight_gain", or "maintenance").
        somatotype (str): The user's somatotype loaded from the classification file.
        diet_data (list): A list of dictionaries containing diet templates loaded from a CSV file.

    Methods:
        load_somatotype():
            Loads the somatotype classification from the output_classification.csv file.

        load_diet_data(filename):
            Loads diet templates from a CSV file and returns them as a list of dictionaries.

        calculate_macros():
            Calculates the recommended macronutrient targets and suggested foods based on the user's data, somatotype, and goal.

        display_recommendations():
            Displays the recommended macronutrient targets and suggested foods to the user.
    """
    
    def __init__(self, user_data, goal):
        self.user_data = user_data
        self.goal = goal
        self.somatotype = self.load_somatotype()
        self.diet_data = self.load_diet_data("diet_templates.csv")

    def load_somatotype(self):
        """
        Load somatotype classification from the output_classification.csv file.
        """
        classification_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
        df = pd.read_csv(classification_file)
        if "Somatotype" not in df.columns:
            raise KeyError("Somatotype column not found in the classification file.")
        return df["Somatotype"].iloc[0].lower()

    def load_diet_data(self, filename):
        """
        Load diet templates from a CSV file.
        """
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def calculate_macros(self):
        """
        Calculate macronutrient targets and suggested foods based on somatotype and goal.
        """
        weight = self.user_data["weight_kg"]
        height = self.user_data["height_cm"]
        age = self.user_data["age"]
        sex = self.user_data["sex"]
        activity_level = self.user_data["activity_level"]

        bmr = calculate_bmr(weight, height, age, sex)
        tdee = bmr * get_activity_multiplier(activity_level)

        if self.goal == "weight_loss":
            calories = tdee - 500
        elif self.goal == "weight_gain":
            calories = tdee + 500
        else:
            calories = tdee

        for row in self.diet_data:
            if row["somatotype"] == self.somatotype and row["goal"] == self.goal:
                macros = {
                    "calories": round(calories),
                    "protein": int(row["protein_g"]),
                    "carbs": int(row["carbs_g"]),
                    "fat": int(row["fats_g"]),
                }
                food_list = row["foods"].split(", ")
                return macros, food_list
        return None, None

    def display_recommendations(self):
        """
        Display the recommended macronutrient targets and suggested foods.
        """
        macros, foods = self.calculate_macros()
        if macros and foods:
            print("Recommended Macronutrient Targets:")
            for k, v in macros.items():
                print(f" {k}: {v}")

            print("\nSuggested Foods:")
            for food in foods:
                print(f" - {food}")
        else:
            print("No recommendation found for the given somatotype and goal.")


# -----------------------------
# Example Usage
# -----------------------------

user_data = {
    "weight_kg": 70,
    "height_cm": 175,
    "age": 28,
    "sex": "male",
    "activity_level": "moderate",
}

goal = "weight_loss"

recommender = Recommender(user_data, goal)
recommender.display_recommendations()
