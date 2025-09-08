import pandas as pd

# Load nutrient definitions
nutrient_defs = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/nutrient.csv')

print("CHECKING FNDDS NUTRIENT IDs...")
print("=" * 50)

# Check key nutrients we need
key_searches = {
    'Energy': ['energy', 'kcal'],
    'Protein': ['protein'],
    'Carbohydrates': ['carbohydrate'],
    'Fat': ['fat', 'lipid'],
    'Fiber': ['fiber'],
    'Sugar': ['sugar'],
    'Sodium': ['sodium']
}

for nutrient_type, search_terms in key_searches.items():
    print(f"\n{nutrient_type.upper()}:")
    for term in search_terms:
        matches = nutrient_defs[nutrient_defs['name'].str.contains(term, case=False, na=False)]
        if len(matches) > 0:
            print(f"  {term} matches:")
            for _, row in matches.head(3).iterrows():
                print(f"    ID {row['id']}: {row['name']} ({row['unit_name']})")

print(f"\nTotal nutrients available: {len(nutrient_defs)}")
