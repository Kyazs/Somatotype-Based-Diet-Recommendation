#!/usr/bin/env python3
"""
Quick script to check the actual columns in the FNDDS nutrients DataFrame
"""

import pandas as pd
import os

# Define file paths
base_path = "../FoodData_Central_survey_food_csv_2024-10-31"
nutrition_file = os.path.join(base_path, "food_nutrient.csv")

print("🔍 Checking FNDDS nutrition data structure...")

# Load nutrition data
nutrients_df = pd.read_csv(nutrition_file)

print(f"\n📊 Nutrients DataFrame Info:")
print(f"Shape: {nutrients_df.shape}")
print(f"\nColumns: {list(nutrients_df.columns)}")
print(f"\nFirst few rows:")
print(nutrients_df.head())

print(f"\nSample of unique values in key columns:")
if 'nutrient_id' in nutrients_df.columns:
    print(f"nutrient_id samples: {sorted(nutrients_df['nutrient_id'].unique())[:20]}")
if 'nutrient_nbr' in nutrients_df.columns:
    print(f"nutrient_nbr samples: {sorted(nutrients_df['nutrient_nbr'].unique())[:20]}")

# Check for our target nutrients
target_nutrient_ids = [208, 203, 204, 205, 291, 269, 307]
print(f"\n🎯 Checking for target nutrients:")

for col in nutrients_df.columns:
    if 'nutrient' in col.lower():
        matching = nutrients_df[nutrients_df[col].isin(target_nutrient_ids)]
        print(f"Column '{col}': {len(matching)} matches for target nutrients")
        if len(matching) > 0:
            print(f"  Sample matches: {matching[col].unique()[:10]}")
