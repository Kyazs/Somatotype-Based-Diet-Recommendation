import pandas as pd

nutrient_defs = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/nutrient.csv')

print("KEY NUTRIENTS FOR FNDDS PROCESSING:")
print("=" * 50)

# Check key nutrients we need
key_patterns = ['energy', 'protein', 'carbohydrate', 'lipid', 'fat', 'fiber', 'sugar', 'sodium']

for pattern in key_patterns:
    matches = nutrient_defs[nutrient_defs['name'].str.contains(pattern, case=False, na=False)]
    if len(matches) > 0:
        print(f'\n{pattern.upper()}:')
        print(matches[['nutrient_nbr', 'name', 'unit_name']].to_string(index=False))
