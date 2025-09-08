#!/usr/bin/env python3
"""
Create Optimized Diet Recommendation Database
Refines FNDDS data specifically for somatotype-based individual diet recommendations
"""

import pandas as pd
import numpy as np
import re


def create_optimized_diet_database():
    """
    Create a refined dataset optimized for somatotype-based diet recommendations
    - Removes redundant/unsuitable foods
    - Optimizes for weight goals (gain/maintain/lose)
    - Enhances somatotype categorization
    - Adds recommendation scores
    """

    print("🎯 CREATING OPTIMIZED DIET RECOMMENDATION DATABASE")
    print("=" * 60)

    # Load the processed FNDDS data
    df = pd.read_csv("fndds_premium_nutrition_database.csv")
    print(f"📂 Loaded {len(df):,} foods from FNDDS processed data")

    # ============================================================================
    # STEP 1: Remove Unsuitable Foods
    # ============================================================================
    print("\n🚫 STEP 1: Removing unsuitable foods...")

    initial_count = len(df)

    # Remove baby foods (not for adult recommendations)
    df = df[
        ~df["Food_Item"].str.contains("Baby|baby|Formula|formula", na=False, case=False)
    ]
    print(f"   ❌ Removed baby foods: {initial_count - len(df)} foods")

    # Remove very low nutritional value foods
    df = df[~((df["Calories_kcal"] < 20) & (df["Protein_g"] < 1) & (df["Fiber_g"] < 1))]
    low_nutrition_removed = initial_count - len(df)

    # Remove alcoholic beverages (not suitable for general diet recommendations)
    df = df[
        ~df["Food_Item"].str.contains(
            "Alcohol|Beer|Wine|Liquor|alcoholic", na=False, case=False
        )
    ]

    # Remove very niche/regional foods that aren't widely available
    niche_patterns = ["Atole(?! De)", "Traditional", "Ethnic", "Regional"]
    for pattern in niche_patterns:
        df = df[
            ~df["Food_Item"].str.contains(pattern, na=False, case=False, regex=True)
        ]

    print(f"   ❌ Total foods removed: {initial_count - len(df)}")
    print(f"   ✅ Foods remaining: {len(df):,}")

    # ============================================================================
    # STEP 2: Deduplicate Similar Foods
    # ============================================================================
    print("\n🔄 STEP 2: Deduplicating similar foods...")

    def deduplicate_foods(df):
        """Remove very similar foods, keeping the most nutritionally complete"""

        # Group similar foods by simplified names
        df["simplified_name"] = (
            df["Food_Item"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
        )
        df["simplified_name"] = (
            df["simplified_name"].str.replace(r"\s+", " ", regex=True).str.strip()
        )

        duplicates_removed = 0
        foods_to_remove = []

        # Find groups of similar foods
        for name_group in df.groupby("simplified_name"):
            name, group = name_group
            if len(group) > 1:
                # Keep the food with the best nutritional completeness
                group["completeness_score"] = (
                    (group["Protein_g"] > 0).astype(int)
                    + (group["Carbohydrates_g"] > 0).astype(int)
                    + (group["Fat_g"] > 0).astype(int)
                    + (group["Fiber_g"] > 0).astype(int)
                    + (group["Nutrient_Density_Score"] > 0).astype(int)
                )

                # Keep the most complete one
                best_food = group.loc[group["completeness_score"].idxmax()]
                foods_to_remove.extend(
                    group[group.index != best_food.name].index.tolist()
                )
                duplicates_removed += len(group) - 1

        df_dedup = df.drop(foods_to_remove)
        df_dedup = df_dedup.drop("simplified_name", axis=1)

        print(f"   🔄 Deduplicated {duplicates_removed} similar foods")
        return df_dedup

    df = deduplicate_foods(df)
    print(f"   ✅ Unique foods after deduplication: {len(df):,}")

    # ============================================================================
    # STEP 3: Enhanced Somatotype Categorization
    # ============================================================================
    print("\n🧬 STEP 3: Enhanced somatotype categorization...")

    def enhanced_somatotype_categorization(
        food_name, calories, protein, carbs, fat, fiber, sugar, sodium
    ):
        """
        Enhanced categorization for somatotype-based recommendations
        """
        food_lower = food_name.lower() if pd.notna(food_name) else ""

        # Calculate ratios for better categorization
        protein_cal_ratio = (protein * 4) / max(calories, 1) if calories > 0 else 0
        fiber_per_100cal = (fiber / max(calories, 1)) * 100 if calories > 0 else 0

        # LEAN PROTEINS (High protein, low fat) - Ideal for all somatotypes
        if (protein >= 18 and protein_cal_ratio >= 0.6) or any(
            word in food_lower
            for word in [
                "chicken breast",
                "turkey breast",
                "fish",
                "cod",
                "tuna",
                "salmon",
                "tofu",
                "egg white",
            ]
        ):
            return "lean_proteins"

        # COMPLETE PROTEINS (Good protein with some fat) - Great for mesomorphs
        elif protein >= 15 and protein_cal_ratio >= 0.4:
            return "complete_proteins"

        # COMPLEX CARBS (High carbs, good fiber, moderate calories) - Best for pre/post workout
        elif (carbs >= 15 and fiber >= 3 and calories <= 350) or any(
            word in food_lower
            for word in ["oats", "quinoa", "brown rice", "sweet potato", "whole grain"]
        ):
            return "complex_carbs"

        # QUICK CARBS (High carbs, low fiber) - For immediate energy
        elif carbs >= 15 and fiber < 2:
            return "quick_carbs"

        # HEALTHY FATS (High fat, good nutritional profile) - Essential for hormones
        elif (fat >= 10 and sodium < 400) or any(
            word in food_lower
            for word in ["avocado", "nuts", "seeds", "olive oil", "salmon"]
        ):
            return "healthy_fats"

        # VEGETABLES (Low calorie, high fiber/nutrients) - Perfect for endomorphs
        elif (calories <= 80 and fiber >= 2) or any(
            word in food_lower
            for word in ["broccoli", "spinach", "kale", "lettuce", "cucumber", "tomato"]
        ):
            return "vegetables"

        # FRUITS (Natural sugars, vitamins) - Good for all, timing matters
        elif any(
            word in food_lower
            for word in ["apple", "banana", "berry", "orange", "grape", "fruit"]
        ):
            return "fruits"

        # DAIRY PROTEINS (Protein + calcium) - Good recovery foods
        elif (
            any(
                word in food_lower
                for word in ["milk", "yogurt", "cheese", "cottage cheese"]
            )
            and protein >= 8
        ):
            return "dairy_proteins"

        # ENERGY DENSE (High calories, good for ectomorphs)
        elif calories >= 350:
            return "energy_dense"

        # WEIGHT LOSS FRIENDLY (Low calorie, high satiety)
        elif calories <= 100 and (protein >= 5 or fiber >= 3):
            return "weight_loss_friendly"

        # PROCESSED/SNACKS (Limit these)
        elif sodium >= 500 or any(
            word in food_lower
            for word in ["chips", "cookies", "candy", "soda", "processed"]
        ):
            return "processed_foods"

        else:
            return "balanced_foods"

    # Apply enhanced categorization
    df["Enhanced_Category"] = df.apply(
        lambda row: enhanced_somatotype_categorization(
            row["Food_Item"],
            row["Calories_kcal"],
            row["Protein_g"],
            row["Carbohydrates_g"],
            row["Fat_g"],
            row["Fiber_g"],
            row["Sugars_g"],
            row["Sodium_mg"],
        ),
        axis=1,
    )

    print("   Enhanced category distribution:")
    for category, count in df["Enhanced_Category"].value_counts().items():
        print(f"      {category}: {count} foods")

    # ============================================================================
    # STEP 4: Add Goal-Specific Recommendation Scores
    # ============================================================================
    print("\n🎯 STEP 4: Adding goal-specific recommendation scores...")

    def calculate_goal_scores(row):
        """Calculate recommendation scores for different goals"""

        calories = row["Calories_kcal"]
        protein = row["Protein_g"]
        carbs = row["Carbohydrates_g"]
        fat = row["Fat_g"]
        fiber = row["Fiber_g"]
        sodium = row["Sodium_mg"]

        # Weight Loss Score (0-10)
        weight_loss_score = 0
        if calories <= 150:
            weight_loss_score += 3
        elif calories <= 250:
            weight_loss_score += 2
        if protein >= 10:
            weight_loss_score += 2
        if fiber >= 3:
            weight_loss_score += 2
        if sodium <= 300:
            weight_loss_score += 1
        if fat <= 10:
            weight_loss_score += 1

        # Weight Gain Score (0-10)
        weight_gain_score = 0
        if calories >= 250:
            weight_gain_score += 3
        elif calories >= 150:
            weight_gain_score += 2
        if protein >= 8:
            weight_gain_score += 2
        if fat >= 5:
            weight_gain_score += 2
        if carbs >= 15:
            weight_gain_score += 1
        if sodium <= 400:
            weight_gain_score += 1

        # Maintenance Score (0-10)
        maintenance_score = 0
        if 100 <= calories <= 300:
            maintenance_score += 3
        if protein >= 5:
            maintenance_score += 2
        if fiber >= 2:
            maintenance_score += 2
        if sodium <= 350:
            maintenance_score += 1
        if 5 <= fat <= 15:
            maintenance_score += 1
        if row["Nutrient_Density_Score"] > 1.5:
            maintenance_score += 1

        return pd.Series(
            {
                "Weight_Loss_Score": min(weight_loss_score, 10),
                "Weight_Gain_Score": min(weight_gain_score, 10),
                "Maintenance_Score": min(maintenance_score, 10),
            }
        )

    goal_scores = df.apply(calculate_goal_scores, axis=1)
    df = pd.concat([df, goal_scores], axis=1)

    # ============================================================================
    # STEP 5: Add Somatotype Suitability Scores
    # ============================================================================
    print("\n🧬 STEP 5: Adding somatotype suitability scores...")

    def calculate_somatotype_scores(row):
        """Calculate suitability scores for each somatotype"""

        category = row["Enhanced_Category"]
        calories = row["Calories_kcal"]
        protein = row["Protein_g"]
        carbs = row["Carbohydrates_g"]
        fat = row["Fat_g"]
        fiber = row["Fiber_g"]

        # Ectomorph Score (needs high calories, carbs)
        ecto_score = 0
        if category in ["energy_dense", "complex_carbs", "healthy_fats"]:
            ecto_score += 4
        elif category in ["complete_proteins", "dairy_proteins"]:
            ecto_score += 3
        if calories >= 300:
            ecto_score += 2
        if carbs >= 20:
            ecto_score += 2
        if fat >= 8:
            ecto_score += 1

        # Mesomorph Score (balanced, high protein)
        meso_score = 0
        if category in ["lean_proteins", "complete_proteins", "complex_carbs"]:
            meso_score += 4
        elif category in ["dairy_proteins", "healthy_fats"]:
            meso_score += 3
        if protein >= 15:
            meso_score += 3
        if 150 <= calories <= 350:
            meso_score += 2

        # Endomorph Score (low calorie, high fiber/protein)
        endo_score = 0
        if category in ["vegetables", "weight_loss_friendly", "lean_proteins"]:
            endo_score += 4
        elif category in ["fruits", "complete_proteins"]:
            endo_score += 3
        if calories <= 150:
            endo_score += 3
        if fiber >= 4:
            endo_score += 2
        if protein >= 12:
            endo_score += 2

        return pd.Series(
            {
                "Ectomorph_Score": min(ecto_score, 10),
                "Mesomorph_Score": min(meso_score, 10),
                "Endomorph_Score": min(endo_score, 10),
            }
        )

    somatotype_scores = df.apply(calculate_somatotype_scores, axis=1)
    df = pd.concat([df, somatotype_scores], axis=1)

    # ============================================================================
    # STEP 6: Add Meal Timing Recommendations
    # ============================================================================
    print("\n⏰ STEP 6: Adding meal timing recommendations...")

    def get_meal_timing(row):
        """Recommend optimal meal timing for each food"""

        category = row["Enhanced_Category"]
        calories = row["Calories_kcal"]
        carbs = row["Carbohydrates_g"]
        protein = row["Protein_g"]

        timings = []

        # Breakfast suitable
        if category in ["complex_carbs", "fruits", "dairy_proteins"] or (
            carbs >= 15 and calories <= 300
        ):
            timings.append("breakfast")

        # Pre-workout suitable
        if category in ["quick_carbs", "fruits"] or (carbs >= 10 and calories <= 200):
            timings.append("pre_workout")

        # Post-workout suitable
        if (
            category in ["lean_proteins", "complete_proteins", "dairy_proteins"]
            or protein >= 15
        ):
            timings.append("post_workout")

        # Lunch/Dinner suitable
        if category in [
            "lean_proteins",
            "complete_proteins",
            "vegetables",
            "balanced_foods",
        ] or (protein >= 8 and calories >= 100):
            timings.extend(["lunch", "dinner"])

        # Snack suitable
        if calories <= 200 and (protein >= 5 or category in ["fruits", "healthy_fats"]):
            timings.append("snack")

        return ", ".join(timings) if timings else "flexible"

    df["Meal_Timing"] = df.apply(get_meal_timing, axis=1)

    # ============================================================================
    # STEP 7: Add Practical Recommendations
    # ============================================================================
    print("\n💡 STEP 7: Adding practical recommendations...")

    # Add portion recommendations
    def get_portion_recommendation(calories, category):
        """Recommend typical portion sizes"""
        if category in ["vegetables"]:
            return "150-200g"
        elif category in ["lean_proteins", "complete_proteins"]:
            return "100-150g"
        elif category in ["complex_carbs"]:
            return "80-120g"
        elif category in ["fruits"]:
            return "1 medium or 100g"
        elif category in ["healthy_fats"]:
            return "30-50g"
        elif category in ["dairy_proteins"]:
            return "150-200ml"
        else:
            return "100g"

    df["Portion_Recommendation"] = df.apply(
        lambda row: get_portion_recommendation(
            row["Calories_kcal"], row["Enhanced_Category"]
        ),
        axis=1,
    )

    # ============================================================================
    # STEP 8: Final Filtering and Ranking
    # ============================================================================
    print("\n🏆 STEP 8: Final filtering and ranking...")

    # Remove foods with very low recommendation scores across all goals
    df["Total_Score"] = (
        df["Weight_Loss_Score"] + df["Weight_Gain_Score"] + df["Maintenance_Score"]
    )
    df = df[df["Total_Score"] >= 5]  # Keep foods with reasonable utility

    # Sort by overall recommendation quality
    df["Overall_Quality"] = (
        df["Nutrient_Density_Score"] * 0.3
        + df["Total_Score"] * 0.4
        + (df["Ectomorph_Score"] + df["Mesomorph_Score"] + df["Endomorph_Score"]) * 0.3
    )

    df = df.sort_values("Overall_Quality", ascending=False)

    # Reset index
    df = df.reset_index(drop=True)

    print(f"✅ Final optimized dataset: {len(df):,} foods")

    # ============================================================================
    # STEP 9: Save Optimized Dataset
    # ============================================================================
    print("\n💾 STEP 9: Saving optimized dataset...")

    # Reorder columns for better usability
    columns_order = [
        "Food_Item",
        "Enhanced_Category",
        "Calories_kcal",
        "Protein_g",
        "Carbohydrates_g",
        "Fat_g",
        "Fiber_g",
        "Sugars_g",
        "Sodium_mg",
        "Weight_Loss_Score",
        "Weight_Gain_Score",
        "Maintenance_Score",
        "Ectomorph_Score",
        "Mesomorph_Score",
        "Endomorph_Score",
        "Meal_Timing",
        "Portion_Recommendation",
        "Overall_Quality",
        "Nutrient_Density_Score",
        "Protein_Efficiency",
    ]

    # Add any remaining columns
    remaining_cols = [col for col in df.columns if col not in columns_order]
    final_columns = columns_order + remaining_cols

    df_final = df[final_columns]

    # Save optimized dataset
    df_final.to_csv("optimized_diet_recommendation_database.csv", index=False)

    # Save category-specific datasets
    for category in df_final["Enhanced_Category"].unique():
        category_df = df_final[df_final["Enhanced_Category"] == category]
        filename = f"foods_{category}.csv"
        category_df.to_csv(filename, index=False)
        print(f"   📁 Saved {filename}: {len(category_df)} foods")

    # Create summary report
    with open("optimization_report.txt", "w", encoding="utf-8") as f:
        f.write("OPTIMIZED DIET RECOMMENDATION DATABASE REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Original FNDDS foods: 5,403\n")
        f.write(f"Optimized foods: {len(df_final):,}\n")
        f.write(
            f"Reduction: {5403 - len(df_final):,} foods ({((5403 - len(df_final))/5403)*100:.1f}%)\n\n"
        )

        f.write("ENHANCED CATEGORY DISTRIBUTION:\n")
        for category, count in df_final["Enhanced_Category"].value_counts().items():
            percentage = (count / len(df_final)) * 100
            f.write(f"  {category}: {count} foods ({percentage:.1f}%)\n")

        f.write(f"\nGOAL SUITABILITY:\n")
        f.write(
            f"  High weight loss score (>=7): {len(df_final[df_final['Weight_Loss_Score'] >= 7])}\n"
        )
        f.write(
            f"  High weight gain score (>=7): {len(df_final[df_final['Weight_Gain_Score'] >= 7])}\n"
        )
        f.write(
            f"  High maintenance score (>=7): {len(df_final[df_final['Maintenance_Score'] >= 7])}\n"
        )

        f.write(f"\nSOMATOTYPE SUITABILITY:\n")
        f.write(
            f"  High ectomorph score (>=7): {len(df_final[df_final['Ectomorph_Score'] >= 7])}\n"
        )
        f.write(
            f"  High mesomorph score (>=7): {len(df_final[df_final['Mesomorph_Score'] >= 7])}\n"
        )
        f.write(
            f"  High endomorph score (>=7): {len(df_final[df_final['Endomorph_Score'] >= 7])}\n"
        )

    print("✅ Saved optimization_report.txt")

    return df_final


if __name__ == "__main__":
    print("🚀 Starting optimization process...")
    optimized_df = create_optimized_diet_database()

    print(f"\n🎉 OPTIMIZATION COMPLETE!")
    print(f"📊 Created optimized database with {len(optimized_df):,} foods")
    print(f"🎯 Ready for somatotype-based diet recommendations!")
    print(f"📁 Files created:")
    print(f"   • optimized_diet_recommendation_database.csv")
    print(f"   • foods_[category].csv (category-specific files)")
    print(f"   • optimization_report.txt")
