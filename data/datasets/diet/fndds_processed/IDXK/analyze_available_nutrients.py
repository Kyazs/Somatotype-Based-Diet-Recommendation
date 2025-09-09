import pandas as pd

# Load data
nutrients_df = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/food_nutrient.csv')
nutrient_defs = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/nutrient.csv')

print("FNDDS NUTRITION ANALYSIS")
print("=" * 40)

# Get all unique nutrient IDs present in the data
available_nutrient_ids = set(nutrients_df['nutrient_id'].unique())
print(f"Total unique nutrient IDs in data: {len(available_nutrient_ids)}")

# Show first 20 nutrient IDs
print(f"First 20 nutrient IDs: {sorted(list(available_nutrient_ids))[:20]}")

# Check which of our target nutrients are available
target_nutrients = [1008, 1003, 1005, 1004, 1079, 1063, 1093, 1258, 1253]
available_targets = [nid for nid in target_nutrients if nid in available_nutrient_ids]
print(f"Target nutrients available: {available_targets}")

# Get definitions for all available nutrients
available_defs = nutrient_defs[nutrient_defs['id'].isin(available_nutrient_ids)]

print(f"\nAll available nutrient definitions ({len(available_defs)}):")
print(available_defs[['id', 'name', 'unit_name']].to_string(index=False, max_rows=50))

# Find nutrients by name patterns
print("\nNUTRIENTS BY NAME PATTERNS:")
patterns = ['energy', 'protein', 'carbohydrate', 'fat', 'fiber', 'sugar', 'sodium']
for pattern in patterns:
    matches = available_defs[available_defs['name'].str.contains(pattern, case=False, na=False)]
    if len(matches) > 0:
        print(f"\n{pattern.upper()}:")
        print(matches[['id', 'name', 'unit_name']].to_string(index=False))
