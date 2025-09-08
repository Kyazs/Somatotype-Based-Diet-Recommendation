#!/usr/bin/env python3
"""
Analyze FNDDS processed data for redundancies and optimization opportunities
for somatotype-based diet recommendations
"""

import pandas as pd
import numpy as np
from collections import Counter

def analyze_dataset_quality():
    """Analyze the current FNDDS dataset for issues and redundancies"""
    
    print("🔍 ANALYZING FNDDS DATASET FOR DIET RECOMMENDATION OPTIMIZATION")
    print("=" * 70)
    
    # Load the processed dataset
    df = pd.read_csv('fndds_premium_nutrition_database.csv')
    
    print(f"📊 Current dataset: {len(df):,} foods")
    print(f"📋 Categories: {df['Somatotype_Category'].nunique()}")
    
    # 1. ANALYZE REDUNDANCIES
    print("\n🔍 REDUNDANCY ANALYSIS:")
    print("-" * 50)
    
    # Similar food names
    food_names = df['Food_Item'].str.lower().str.strip()
    
    # Find foods with very similar names
    similar_groups = []
    for i, food in enumerate(food_names):
        if pd.isna(food):
            continue
        similar = food_names[food_names.str.contains(food[:10], na=False, regex=False)]
        if len(similar) > 1:
            similar_groups.append(list(similar.unique()))
    
    # Count baby foods, beverages, and niche items
    baby_foods = df[df['Food_Item'].str.contains('Baby|baby', na=False)]
    atole_variations = df[df['Food_Item'].str.contains('Atole', na=False)]
    juice_variations = df[df['Food_Item'].str.contains('Juice', na=False)]
    
    print(f"👶 Baby foods: {len(baby_foods)} (not suitable for adult diet recommendations)")
    print(f"🥤 Atole variations: {len(atole_variations)} (regional specific)")
    print(f"🧃 Juice variations: {len(juice_variations)} (many similar)")
    
    # 2. CATEGORY DISTRIBUTION ANALYSIS
    print(f"\n📊 CATEGORY DISTRIBUTION:")
    print("-" * 50)
    category_counts = df['Somatotype_Category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {category}: {count:,} foods ({percentage:.1f}%)")
    
    # 3. NUTRITIONAL QUALITY ANALYSIS
    print(f"\n🏆 NUTRITIONAL QUALITY ANALYSIS:")
    print("-" * 50)
    
    # Foods with very low nutritional value
    low_nutrition = df[
        (df['Calories_kcal'] < 20) | 
        ((df['Protein_g'] < 1) & (df['Fiber_g'] < 1) & (df['Fat_g'] < 1))
    ]
    print(f"⚠️  Low nutritional value foods: {len(low_nutrition)}")
    
    # High sodium processed foods
    high_sodium = df[df['Sodium_mg'] > 800]  # >800mg sodium per 100g
    print(f"🧂 High sodium foods: {len(high_sodium)} (may need filtering for health)")
    
    # Very high calorie foods (>500 kcal per 100g)
    very_high_cal = df[df['Calories_kcal'] > 500]
    print(f"🔥 Very high calorie foods: {len(very_high_cal)} (good for ectomorphs)")
    
    # High protein foods (>20g per 100g)
    high_protein = df[df['Protein_g'] > 20]
    print(f"💪 High protein foods: {len(high_protein)} (good for mesomorphs)")
    
    # High fiber foods (>5g per 100g)
    high_fiber = df[df['Fiber_g'] > 5]
    print(f"🌾 High fiber foods: {len(high_fiber)} (good for endomorphs)")
    
    # 4. GOAL-SPECIFIC ANALYSIS
    print(f"\n🎯 GOAL-SPECIFIC SUITABILITY:")
    print("-" * 50)
    
    # Weight loss friendly (low calorie, high fiber/protein)
    weight_loss_friendly = df[
        (df['Calories_kcal'] < 200) & 
        ((df['Protein_g'] > 10) | (df['Fiber_g'] > 3))
    ]
    print(f"📉 Weight loss friendly: {len(weight_loss_friendly)} foods")
    
    # Weight gain friendly (high calorie, good macros)
    weight_gain_friendly = df[
        (df['Calories_kcal'] > 250) & 
        (df['Protein_g'] > 5)
    ]
    print(f"📈 Weight gain friendly: {len(weight_gain_friendly)} foods")
    
    # Maintenance friendly (balanced nutrition)
    maintenance_friendly = df[
        (df['Calories_kcal'].between(100, 300)) & 
        (df['Protein_g'] > 5) & 
        (df['Nutrient_Density_Score'] > 1.5)
    ]
    print(f"⚖️  Maintenance friendly: {len(maintenance_friendly)} foods")
    
    # 5. PRACTICAL DIET PLANNING ANALYSIS
    print(f"\n🍽️ PRACTICAL DIET PLANNING:")
    print("-" * 50)
    
    # Common foods people actually eat
    common_foods = df[
        ~df['Food_Item'].str.contains('Baby|Formula|Atole|Traditional|Ethnic', na=False, case=False)
    ]
    print(f"🏠 Common/accessible foods: {len(common_foods)}")
    
    # Complete nutrition profile foods
    complete_nutrition = df[
        (df['Protein_g'] > 0) & 
        (df['Carbohydrates_g'] > 0) & 
        (df['Fat_g'] >= 0) & 
        (df['Calories_kcal'] > 0)
    ]
    print(f"📋 Complete nutrition profile: {len(complete_nutrition)}")
    
    # 6. RECOMMENDATIONS FOR OPTIMIZATION
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    print("-" * 50)
    
    # Foods to remove
    foods_to_remove = len(baby_foods) + len(low_nutrition)
    print(f"❌ Recommended for removal: {foods_to_remove} foods")
    print("   - Baby foods (not for adult recommendations)")
    print("   - Very low nutritional value foods")
    print("   - Duplicate/very similar foods")
    
    # Foods to prioritize
    priority_foods = df[
        (df['Nutrient_Density_Score'] > 1.0) & 
        (df['Calories_kcal'] > 50) &
        ~df['Food_Item'].str.contains('Baby|Formula', na=False, case=False)
    ]
    print(f"⭐ Priority foods for recommendations: {len(priority_foods)}")
    
    # Missing categories
    print(f"\n🎯 SOMATOTYPE OPTIMIZATION NEEDS:")
    print("-" * 50)
    print("For Ectomorphs (weight gain):")
    print(f"   - Need more calorie-dense foods: {len(df[df['Calories_kcal'] > 400])}")
    print(f"   - Healthy weight-gain foods needed")
    
    print("For Mesomorphs (muscle building):")
    print(f"   - High protein foods available: {len(high_protein)}")
    print(f"   - Need more complete protein sources")
    
    print("For Endomorphs (weight management):")
    print(f"   - Low-calorie foods available: {len(df[df['Calories_kcal'] < 100])}")
    print(f"   - High fiber foods available: {len(high_fiber)}")
    
    return {
        'total_foods': len(df),
        'baby_foods': len(baby_foods),
        'low_nutrition': len(low_nutrition),
        'high_quality': len(priority_foods),
        'weight_loss_suitable': len(weight_loss_friendly),
        'weight_gain_suitable': len(weight_gain_friendly),
        'maintenance_suitable': len(maintenance_friendly)
    }

if __name__ == "__main__":
    analysis_results = analyze_dataset_quality()
    print(f"\n✅ Analysis complete!")
    print(f"📈 Dataset optimization potential: {analysis_results['baby_foods'] + analysis_results['low_nutrition']} foods can be removed")
    print(f"🎯 High-quality foods for recommendations: {analysis_results['high_quality']}")
