import pandas as pd

# Load the tables
nutrients_df = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/food_nutrient.csv')
foods_df = pd.read_csv('../FoodData_Central_survey_food_csv_2024-10-31/food.csv')

print("DEBUGGING FNDDS NUTRITION DATA...")
print("=" * 50)

# Check total nutrition records
print(f"Total nutrition records: {len(nutrients_df):,}")

# Check which foods have nutrition data
fndds_foods = foods_df[foods_df['data_type'] == 'survey_fndds_food']
print(f"FNDDS foods: {len(fndds_foods):,}")

# Check how many FNDDS foods have nutrition data
fndds_food_ids = fndds_foods['fdc_id'].tolist()
fndds_nutrition = nutrients_df[nutrients_df['fdc_id'].isin(fndds_food_ids)]
print(f"FNDDS nutrition records: {len(fndds_nutrition):,}")

# Check unique foods with nutrition data
foods_with_nutrition = fndds_nutrition['fdc_id'].nunique()
print(f"FNDDS foods with nutrition data: {foods_with_nutrition:,}")

# Check key nutrients
key_nutrients = [1008, 1003, 1005, 1004, 1079, 1063, 1093]
for nutrient_id in key_nutrients:
    count = fndds_nutrition[fndds_nutrition['nutrient_id'] == nutrient_id]['fdc_id'].nunique()
    print(f"Foods with nutrient {nutrient_id}: {count:,}")

# Show sample nutrition data
print("\nSAMPLE FNDDS NUTRITION DATA:")
print(fndds_nutrition.head(10).to_string())

# Check if any food has Energy (1008)
energy_foods = fndds_nutrition[fndds_nutrition['nutrient_id'] == 1008]
print(f"\nFoods with Energy data: {len(energy_foods):,}")
if len(energy_foods) > 0:
    print("Sample energy data:")
    print(energy_foods.head().to_string())
