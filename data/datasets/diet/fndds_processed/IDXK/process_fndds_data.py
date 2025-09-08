"""
FNDDS (Food and Nutrient Database for Dietary Studies) Data Processor
=====================================================================

This script processes the USDA FNDDS Survey Food dataset to create a comprehensive,
standardized nutrition database for diet recommendation systems.

FNDDS contains real-world foods that people actually consume in dietary surveys,
making it ideal for practical diet recommendations vs research-focused foundation foods.

Author: Diet Recommendation System
Input: FoodData_Central_survey_food_csv_2024-10-31 files
Outputs: 
    - fndds_premium_nutrition_database.csv (standardized nutrition data)
    - fndds_food_categories_mapping.csv (category relationships)
    - fndds_processing_report.txt (processing summary)
"""

import pandas as pd
import numpy as np
import re
import os
from pathlib import Path

# Set paths
BASE_PATH = Path("../FoodData_Central_survey_food_csv_2024-10-31")
OUTPUT_PATH = Path(".")

print("🍽️ FNDDS SURVEY FOOD DATA PROCESSOR")
print("=" * 60)
print("Processing USDA FNDDS data for diet recommendation system...")

# ============================================================================
# STEP 1: Load Core FNDDS Tables
# ============================================================================
"""
FNDDS Database Schema Overview:
- food.csv: Main food descriptions and IDs
- survey_fndds_food.csv: Survey-specific food codes  
- wweia_food_category.csv: What We Eat In America categories
- food_nutrient.csv: Nutritional composition data
- nutrient.csv: Nutrient definitions and units
"""

print("\n📂 STEP 1: Loading FNDDS core tables...")

try:
    # Load main food table
    foods_df = pd.read_csv(BASE_PATH / "food.csv")
    print(f"✅ Loaded {len(foods_df):,} food items")
    
    # Load survey-specific mappings
    survey_df = pd.read_csv(BASE_PATH / "survey_fndds_food.csv")
    print(f"✅ Loaded {len(survey_df):,} survey food mappings")
    
    # Load WWEIA categories (What We Eat In America)
    wweia_df = pd.read_csv(BASE_PATH / "wweia_food_category.csv")
    print(f"✅ Loaded {len(wweia_df):,} WWEIA food categories")
    
    # Load nutritional data
    nutrients_df = pd.read_csv(BASE_PATH / "food_nutrient.csv")
    print(f"✅ Loaded {len(nutrients_df):,} nutrition records")
    
    # Load nutrient definitions
    nutrient_defs_df = pd.read_csv(BASE_PATH / "nutrient.csv")
    print(f"✅ Loaded {len(nutrient_defs_df):,} nutrient definitions")

except FileNotFoundError as e:
    print(f"❌ Error loading files: {e}")
    print("Please ensure FoodData_Central_survey_food_csv_2024-10-31 folder is in parent directory")
    exit(1)

# ============================================================================
# STEP 2: Filter and Merge Core Food Data
# ============================================================================
"""
Join tables to create comprehensive food dataset:
1. Start with foods table (descriptions)
2. Add survey mappings for food codes
3. Add WWEIA categories for grouping
4. Filter to survey_fndds_food type only (real-world foods)
"""

print("\n🔗 STEP 2: Merging core food data...")

# Filter to only survey FNDDS foods (real-world consumption data)
fndds_foods = foods_df[foods_df['data_type'] == 'survey_fndds_food'].copy()
print(f"📊 Filtered to {len(fndds_foods):,} FNDDS survey foods")

# Merge with survey mappings to get food codes
fndds_foods = fndds_foods.merge(
    survey_df[['fdc_id', 'food_code', 'wweia_category_number']], 
    on='fdc_id', 
    how='left'
)

# Merge with WWEIA categories for food grouping
fndds_foods = fndds_foods.merge(
    wweia_df, 
    left_on='wweia_category_number', 
    right_on='wweia_food_category', 
    how='left'
)

print(f"✅ Successfully merged data for {len(fndds_foods):,} foods")

# ============================================================================
# STEP 3: Extract Key Nutritional Components
# ============================================================================
"""
Extract essential nutrients for diet recommendations (FNDDS nutrient_id system):
- Energy (Calories): 208 (KCAL)
- Protein: 203 (G)  
- Total Carbohydrates: 205 (G)
- Total Fat: 204 (G)
- Fiber: 291 (G)
- Sugars: 269 (G)
- Sodium: 307 (MG)
- Saturated Fat: 606 (G)
- Cholesterol: 601 (MG)
"""

print("\n🔬 STEP 3: Extracting nutritional components...")

# Define key nutrients for diet recommendations (corrected FNDDS nutrient_id)
key_nutrients = {
    208: 'Energy_kcal',        # Energy (KCAL) - nutrient_id 208
    203: 'Protein_g',          # Protein (G) - nutrient_id 203
    205: 'Carbohydrates_g',    # Carbohydrate, by difference (G) - nutrient_id 205
    204: 'Total_Fat_g',        # Total lipid (fat) (G) - nutrient_id 204
    291: 'Fiber_g',            # Fiber, total dietary (G) - nutrient_id 291
    269: 'Sugars_g',           # Total Sugars (G) - nutrient_id 269
    307: 'Sodium_mg',          # Sodium, Na (MG) - nutrient_id 307
    606: 'Saturated_Fat_g',    # Fatty acids, total saturated (G) - nutrient_id 606
    601: 'Cholesterol_mg'      # Cholesterol (MG) - nutrient_id 601
}

# Filter nutrients data to key nutrients only
key_nutrients_data = nutrients_df[
    nutrients_df['nutrient_id'].isin(key_nutrients.keys())
].copy()

print(f"📊 Processing {len(key_nutrients_data):,} nutritional values...")

# Pivot nutrients data to wide format (one row per food)
nutrition_matrix = key_nutrients_data.pivot_table(
    index='fdc_id',
    columns='nutrient_id', 
    values='amount',
    aggfunc='mean'  # Use mean if duplicate entries
).reset_index()

# Rename columns to readable names
nutrition_matrix = nutrition_matrix.rename(columns=key_nutrients)

print(f"✅ Created nutrition matrix for {len(nutrition_matrix):,} foods")

# ============================================================================
# STEP 4: Merge Foods with Nutritional Data
# ============================================================================
"""
Combine food descriptions with nutritional profiles to create master dataset.
Handle missing values appropriately for diet recommendation use.
"""

print("\n🔄 STEP 4: Combining foods with nutrition data...")

# Merge food information with nutritional data
master_df = fndds_foods.merge(nutrition_matrix, on='fdc_id', how='left')

# Check data completeness
total_foods = len(master_df)
complete_nutrition = master_df['Energy_kcal'].notna().sum()
print(f"📊 Total foods: {total_foods:,}")
print(f"📊 Foods with calorie data: {complete_nutrition:,} ({complete_nutrition/total_foods*100:.1f}%)")

# Filter to foods with essential nutrition data (at least calories and protein)
master_df = master_df.dropna(subset=['Energy_kcal', 'Protein_g'])
print(f"✅ Retained {len(master_df):,} foods with essential nutrition data")

# ============================================================================
# STEP 5: Clean and Standardize Food Names
# ============================================================================
"""
Standardize food descriptions for consistency:
- Remove USDA codes and technical terms
- Standardize capitalization
- Clean special characters
- Create user-friendly names
"""

print("\n🧹 STEP 5: Cleaning and standardizing food names...")

def clean_food_description(description):
    """
    Clean USDA food descriptions to user-friendly names.
    
    Example transformations:
    "Milk, reduced fat (2%)" → "Milk Reduced Fat 2%"
    "Beef, ground, 85% lean meat / 15% fat, crumbles, cooked" → "Ground Beef 85% Lean Cooked"
    """
    if pd.isna(description):
        return description
    
    # Convert to string and clean
    name = str(description).strip()
    
    # Remove common USDA descriptors that add noise
    replacements = [
        (r'\b(NFS|NS)\b', ''),  # Not Further Specified, Not Specified
        (r'\b(includes USDA.*?)\b', ''),  # USDA codes
        (r'\([^)]*USDA[^)]*\)', ''),  # USDA in parentheses
        (r'\s+', ' ')  # Multiple spaces to single space
    ]
    
    for pattern, replacement in replacements:
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
    
    # Standardize format
    name = name.strip().title()
    
    # Handle special cases for better readability
    special_cases = {
        'Nfs': 'NFS',
        'Ns': 'NS', 
        'Fat Free': 'Fat-Free',
        'Low Fat': 'Low-Fat',
        'Reduced Fat': 'Reduced-Fat',
        'Non Fat': 'Non-Fat'
    }
    
    for old, new in special_cases.items():
        name = name.replace(old, new)
    
    return name

# Apply cleaning function
master_df['Food_Name_Clean'] = master_df['description'].apply(clean_food_description)

print(f"✅ Cleaned {len(master_df):,} food descriptions")

# ============================================================================
# STEP 6: Create Somatotype-Optimized Food Categories
# ============================================================================
"""
Map WWEIA categories to somatotype-specific food groups based on:
- Macronutrient profiles suitable for each body type
- Metabolic considerations (endomorph, mesomorph, ectomorph)
- Diet recommendation best practices
"""

print("\n🏷️ STEP 6: Creating somatotype-optimized categories...")

def map_wweia_to_somatotype(wweia_description):
    """
    Map WWEIA food categories to somatotype-optimized groups.
    
    Somatotype Categories:
    - lean_proteins: High protein, lower fat (good for all types)
    - healthy_fats: Essential fats (important for ectomorphs)
    - complex_carbs: Slow-release carbs (better for endomorphs)
    - quick_carbs: Fast carbs (good for mesomorphs around workouts)
    - vegetables: Low-calorie, high-nutrient (essential for endomorphs)
    - fruits: Natural sugars + vitamins (moderate for all)
    - dairy_proteins: Protein + calcium sources
    - beverages: Hydration and liquid nutrition
    - energy_dense: High-calorie foods (helpful for ectomorphs)
    - processed_foods: Limit for endomorphs, moderate for others
    """
    
    if pd.isna(wweia_description):
        return 'other'
    
    desc = str(wweia_description).lower()
    
    # Lean Proteins (high protein, moderate fat)
    if any(term in desc for term in [
        'chicken', 'turkey', 'fish', 'seafood', 'lean beef', 'egg whites',
        'protein powder', 'tofu', 'tempeh'
    ]):
        return 'lean_proteins'
    
    # Healthy Fats (essential fatty acids, calorie dense)
    elif any(term in desc for term in [
        'nuts', 'seeds', 'avocado', 'olive', 'fatty fish', 'salmon',
        'oils', 'nut butter'
    ]):
        return 'healthy_fats'
    
    # Complex Carbohydrates (slow release, high fiber)
    elif any(term in desc for term in [
        'oatmeal', 'quinoa', 'brown rice', 'whole grain', 'sweet potato',
        'legumes', 'beans', 'lentils'
    ]):
        return 'complex_carbs'
    
    # Quick Carbohydrates (fast absorption)
    elif any(term in desc for term in [
        'white rice', 'pasta', 'bread', 'cereal', 'crackers', 'bagel',
        'muffin', 'pancake', 'waffle'
    ]):
        return 'quick_carbs'
    
    # Vegetables (low calorie, high nutrients)
    elif any(term in desc for term in [
        'vegetables', 'greens', 'salad', 'broccoli', 'spinach', 'kale',
        'carrots', 'peppers', 'tomato'
    ]):
        return 'vegetables'
    
    # Fruits (natural sugars, vitamins)
    elif any(term in desc for term in [
        'fruit', 'apple', 'banana', 'berries', 'orange', 'grapes',
        'melon', 'citrus'
    ]):
        return 'fruits'
    
    # Dairy Proteins (protein + calcium)
    elif any(term in desc for term in [
        'milk', 'yogurt', 'cheese', 'cottage cheese', 'dairy'
    ]):
        return 'dairy_proteins'
    
    # Beverages (hydration, liquid nutrition)
    elif any(term in desc for term in [
        'water', 'tea', 'coffee', 'juice', 'smoothie', 'shake',
        'beverage', 'drink'
    ]):
        return 'beverages'
    
    # Energy Dense Foods (high calories for weight gain)
    elif any(term in desc for term in [
        'chocolate', 'candy', 'ice cream', 'cake', 'cookies',
        'fried', 'fast food', 'pizza'
    ]):
        return 'energy_dense'
    
    # Processed Foods (limit for weight management)
    elif any(term in desc for term in [
        'processed', 'packaged', 'frozen meal', 'snack food',
        'chips', 'crackers'
    ]):
        return 'processed_foods'
    
    else:
        return 'other'

# Apply somatotype categorization
master_df['Somatotype_Category'] = master_df['wweia_food_category_description'].apply(map_wweia_to_somatotype)

# Report category distribution
print("\n📊 Somatotype category distribution:")
category_counts = master_df['Somatotype_Category'].value_counts()
for category, count in category_counts.items():
    percentage = (count / len(master_df)) * 100
    print(f"   {category}: {count:,} foods ({percentage:.1f}%)")

# ============================================================================
# STEP 7: Calculate Derived Nutritional Features
# ============================================================================
"""
Calculate additional metrics useful for diet recommendations:
- Macronutrient percentages of total calories
- Nutrient density scores
- Protein efficiency ratios
- Caloric density
"""

print("\n⚙️ STEP 7: Calculating derived nutritional features...")

# Fill missing values with 0 for calculations
nutrition_cols = ['Energy_kcal', 'Protein_g', 'Carbohydrates_g', 'Total_Fat_g', 'Fiber_g']
for col in nutrition_cols:
    master_df[col] = master_df[col].fillna(0)

# Calculate macronutrient percentages (calories from each macro)
master_df['Protein_Calories_Pct'] = (master_df['Protein_g'] * 4) / master_df['Energy_kcal'] * 100
master_df['Carb_Calories_Pct'] = (master_df['Carbohydrates_g'] * 4) / master_df['Energy_kcal'] * 100  
master_df['Fat_Calories_Pct'] = (master_df['Total_Fat_g'] * 9) / master_df['Energy_kcal'] * 100

# Calculate nutrient density (protein + fiber per 100 calories)
master_df['Nutrient_Density_Score'] = (master_df['Protein_g'] + master_df['Fiber_g']) / (master_df['Energy_kcal'] / 100)

# Calculate protein efficiency (protein per calorie)
master_df['Protein_Efficiency'] = master_df['Protein_g'] / master_df['Energy_kcal']

# Handle division by zero and extreme values
for col in ['Protein_Calories_Pct', 'Carb_Calories_Pct', 'Fat_Calories_Pct', 'Nutrient_Density_Score', 'Protein_Efficiency']:
    master_df[col] = master_df[col].replace([np.inf, -np.inf], 0).fillna(0)
    master_df[col] = master_df[col].clip(0, 100 if 'Pct' in col else 10)  # Reasonable upper bounds

print("✅ Calculated derived nutritional features")

# ============================================================================
# STEP 8: Quality Control and Data Validation
# ============================================================================
"""
Apply quality controls to ensure data reliability:
- Remove foods with impossible nutritional values
- Flag foods with suspicious macro ratios
- Ensure minimum data completeness
"""

print("\n🔍 STEP 8: Quality control and validation...")

initial_count = len(master_df)

# Remove foods with impossible values
master_df = master_df[
    (master_df['Energy_kcal'] > 0) &  # Must have calories
    (master_df['Energy_kcal'] < 2000) &  # Reasonable calorie limit per 100g
    (master_df['Protein_g'] >= 0) &
    (master_df['Protein_g'] <= 100) &  # Max 100g protein per 100g food
    (master_df['Total_Fat_g'] >= 0) &
    (master_df['Total_Fat_g'] <= 100) &
    (master_df['Carbohydrates_g'] >= 0) &
    (master_df['Carbohydrates_g'] <= 100)
]

removed_count = initial_count - len(master_df)
print(f"✅ Removed {removed_count:,} foods with impossible values")

# Check macro balance (proteins + carbs + fats should roughly account for calories)
master_df['Calculated_Calories'] = (
    master_df['Protein_g'] * 4 +
    master_df['Carbohydrates_g'] * 4 + 
    master_df['Total_Fat_g'] * 9
)

# Flag foods where calculated calories are very different from reported
master_df['Macro_Balance_Check'] = abs(
    master_df['Energy_kcal'] - master_df['Calculated_Calories']
) / master_df['Energy_kcal'] < 0.5  # Within 50%

balance_issues = (~master_df['Macro_Balance_Check']).sum()
print(f"⚠️  {balance_issues:,} foods have macro balance discrepancies (kept for completeness)")

print(f"✅ Final dataset: {len(master_df):,} high-quality foods")

# ============================================================================
# STEP 9: Create Final Standardized Dataset
# ============================================================================
"""
Create final output dataset with standardized schema matching the 
existing standardized_nutrition_database.csv format for compatibility.
"""

print("\n📋 STEP 9: Creating final standardized dataset...")

# Select and rename columns to match existing schema
final_dataset = master_df[[
    'Food_Name_Clean',
    'Energy_kcal', 
    'Protein_g',
    'Carbohydrates_g',
    'Total_Fat_g',
    'Fiber_g',
    'wweia_food_category_description',
    'Somatotype_Category',
    'Protein_Calories_Pct',
    'Carb_Calories_Pct', 
    'Fat_Calories_Pct',
    'Nutrient_Density_Score',
    'Protein_Efficiency',
    'Sugars_g',
    'Sodium_mg',
    'Saturated_Fat_g',
    'Cholesterol_mg'
]].copy()

# Rename columns to match standard schema
final_dataset = final_dataset.rename(columns={
    'Food_Name_Clean': 'Food_Item',
    'Energy_kcal': 'Calories_kcal',
    'Protein_g': 'Protein_g', 
    'Carbohydrates_g': 'Carbohydrates_g',
    'Total_Fat_g': 'Fat_g',
    'Fiber_g': 'Fiber_g',
    'wweia_food_category_description': 'Original_Category',
    'Somatotype_Category': 'Somatotype_Category'
})

# Sort by somatotype category and food name for organized output
final_dataset = final_dataset.sort_values(['Somatotype_Category', 'Food_Item'])

# Round nutritional values to reasonable precision
nutrition_round_cols = [
    'Calories_kcal', 'Protein_g', 'Carbohydrates_g', 'Fat_g', 'Fiber_g',
    'Protein_Calories_Pct', 'Carb_Calories_Pct', 'Fat_Calories_Pct',
    'Nutrient_Density_Score', 'Protein_Efficiency', 'Sugars_g', 'Sodium_mg',
    'Saturated_Fat_g', 'Cholesterol_mg'
]

for col in nutrition_round_cols:
    if col in final_dataset.columns:
        final_dataset[col] = final_dataset[col].round(2)

print(f"✅ Created final dataset with {len(final_dataset):,} foods")

# ============================================================================
# STEP 10: Save Outputs and Generate Reports
# ============================================================================
"""
Save processed datasets and generate comprehensive processing report.
"""

print("\n💾 STEP 10: Saving outputs...")

# Save main nutrition database
output_file = OUTPUT_PATH / "fndds_premium_nutrition_database.csv"
final_dataset.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")

# Save category mapping for reference
category_mapping = master_df[['wweia_food_category', 'wweia_food_category_description', 'Somatotype_Category']].drop_duplicates()
mapping_file = OUTPUT_PATH / "fndds_food_categories_mapping.csv"
category_mapping.to_csv(mapping_file, index=False)
print(f"✅ Saved: {mapping_file}")

# Generate processing report
report_content = f"""
FNDDS PREMIUM NUTRITION DATABASE PROCESSING REPORT
===============================================
Generated: August 31, 2025
Source: USDA FoodData Central Survey Food (FNDDS) 2024-10-31

DATASET STATISTICS:
- Total foods processed: {len(final_dataset):,}
- Original WWEIA categories: {master_df['wweia_food_category_description'].nunique():,}
- Somatotype categories: {final_dataset['Somatotype_Category'].nunique():,}
- Data completeness: {(final_dataset['Calories_kcal'] > 0).sum() / len(final_dataset) * 100:.1f}%

SOMATOTYPE CATEGORY DISTRIBUTION:
{category_counts.to_string()}

NUTRITIONAL PROFILE SUMMARY:
- Average calories: {final_dataset['Calories_kcal'].mean():.1f} kcal
- Average protein: {final_dataset['Protein_g'].mean():.1f}g
- Average carbohydrates: {final_dataset['Carbohydrates_g'].mean():.1f}g  
- Average fat: {final_dataset['Fat_g'].mean():.1f}g
- Average fiber: {final_dataset['Fiber_g'].mean():.1f}g

DATA QUALITY METRICS:
- Foods removed due to quality issues: {removed_count:,}
- Foods with macro balance discrepancies: {balance_issues:,}
- Final retention rate: {len(final_dataset) / initial_count * 100:.1f}%

FILES GENERATED:
1. fndds_premium_nutrition_database.csv - Main nutrition database
2. fndds_food_categories_mapping.csv - Category relationship mapping
3. fndds_processing_report.txt - This processing report

USAGE NOTES:
- Dataset contains real-world foods from USDA dietary surveys
- Optimized for somatotype-based diet recommendations
- Compatible with existing diet recommendation system schema
- Nutritional values are per 100g unless otherwise specified
"""

report_file = OUTPUT_PATH / "fndds_processing_report.txt"
with open(report_file, 'w') as f:
    f.write(report_content)
print(f"✅ Saved: {report_file}")

# ============================================================================
# PROCESSING COMPLETE
# ============================================================================

print("\n🎉 FNDDS PROCESSING COMPLETE!")
print("=" * 60)
print(f"✅ Successfully processed {len(final_dataset):,} foods from USDA FNDDS")
print(f"✅ Created {final_dataset['Somatotype_Category'].nunique()} somatotype-optimized categories")
print(f"✅ Generated comprehensive nutrition database for diet recommendations")

print(f"\n📁 OUTPUT FILES:")
print(f"   • fndds_premium_nutrition_database.csv ({len(final_dataset):,} foods)")
print(f"   • fndds_food_categories_mapping.csv ({len(category_mapping):,} categories)")
print(f"   • fndds_processing_report.txt (processing summary)")

print(f"\n🚀 Ready for integration with diet recommendation system!")
print("This dataset contains real-world foods that people actually consume,")
print("making it ideal for practical diet recommendations.")
