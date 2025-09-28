"""
PDF Export Utility for Diet Recommendation System
Generates professional PDF reports from diet analysis results
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project directory to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.platypus import PageBreak, KeepTogether, Frame, PageTemplate, NextPageTemplate
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.lib.colors import HexColor
    from PIL import Image as PILImage
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from io import BytesIO
except ImportError as e:
    print(f"PDF export dependencies not installed: {e}")
    print("Please install requirements: pip install -r requirements/pdf_export_requirements.txt")
    sys.exit(1)

# Import project utilities for data loading
try:
    from .database import DatabaseManager 
    from .food_data_loader import FoodDataLoader
    from .exercise_data_loader import ExerciseDataLoader
except ImportError:
    # Fallback imports for direct execution
    from database import DatabaseManager
    from food_data_loader import FoodDataLoader
    from exercise_data_loader import ExerciseDataLoader


class PDFExporter:
    """Professional PDF export utility for diet recommendation reports"""
    
    # Brand colors matching the application theme
    BRAND_PRIMARY = HexColor('#2E5266')
    BRAND_SECONDARY = HexColor('#F8F9FA')
    BRAND_SUCCESS = HexColor('#28A745')
    BRAND_WARNING = HexColor('#FFC107')
    BRAND_GRAY_DARK = HexColor('#343A40')
    BRAND_GRAY_MEDIUM = HexColor('#6C757D')
    BRAND_GRAY_LIGHT = HexColor('#E9ECEF')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Initialize data loaders like the GUI pages do
        self.db_manager = DatabaseManager()
        self.food_loader = FoodDataLoader()
        self.exercise_loader = ExerciseDataLoader()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for consistent formatting"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=self.BRAND_PRIMARY,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=self.BRAND_PRIMARY,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=self.BRAND_GRAY_DARK,
            fontName='Helvetica-Bold'
        ))
        
        # Custom body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=self.BRAND_GRAY_DARK,
            fontName='Helvetica',
            leading=14
        ))
        
        # Highlight box style
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=self.BRAND_PRIMARY,
            fontName='Helvetica-Bold',
            backColor=self.BRAND_SECONDARY,
            borderColor=self.BRAND_PRIMARY,
            borderWidth=1,
            borderPadding=12
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='CustomCaption',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=self.BRAND_GRAY_MEDIUM,
            fontName='Helvetica-Oblique'
        ))
    
    def export_history_detail(self, record_data: Dict[str, Any], output_path: str) -> bool:
        """
        Export history detail page to PDF with images and full analysis
        
        Args:
            record_data: Dictionary containing all record information
            output_path: Path where PDF will be saved
            
        Returns:
            bool: Success status
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )
            
            story = []
            
            # Header section
            self._add_header(story, record_data, include_date=True)
            story.append(Spacer(1, 12))
            
            # Captured images section (if available)
            if self._has_images(record_data):
                self._add_captured_images_section(story, record_data)
                story.append(PageBreak())
            
            # User summary
            self._add_user_summary(story, record_data)
            story.append(Spacer(1, 15))
            
            # Nutrition analysis
            self._add_nutrition_section(story, record_data)
            story.append(Spacer(1, 15))
            
            # Somatotype analysis
            self._add_somatotype_section(story, record_data)
            story.append(PageBreak())
            
            # Diet recommendations
            self._add_diet_recommendations(story, record_data)
            
            # Exercise recommendations
            self._add_exercise_recommendations(story, record_data)
            
            # Footer
            self._add_footer(story, record_data)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error exporting history detail to PDF: {e}")
            return False
    
    def export_current_diet_plan(self, record_data: Dict[str, Any], output_path: str) -> bool:
        """
        Export current diet plan to PDF (without captured images)
        
        Args:
            record_data: Dictionary containing current analysis data
            output_path: Path where PDF will be saved
            
        Returns:
            bool: Success status
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )
            
            story = []
            
            # Header section
            self._add_header(story, record_data, include_date=False)
            story.append(Spacer(1, 12))
            
            # User summary
            self._add_user_summary(story, record_data)
            story.append(Spacer(1, 15))
            
            # Nutrition analysis
            self._add_nutrition_section(story, record_data)
            story.append(Spacer(1, 15))
            
            # Somatotype analysis
            self._add_somatotype_section(story, record_data)
            story.append(PageBreak())
            
            # Diet recommendations
            self._add_diet_recommendations(story, record_data)
            
            # Exercise recommendations
            self._add_exercise_recommendations(story, record_data)
            
            # Footer
            self._add_footer(story, record_data)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error exporting diet plan to PDF: {e}")
            return False
    
    def _add_header(self, story: List, record_data: Dict, include_date: bool = False):
        """Add report header"""
        title = "Your Personalized Diet Plan"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        
        if include_date:
            session_date = record_data.get('session_date', '')
            if session_date:
                formatted_date = self._format_date(session_date)
                subtitle = f"Based on analysis from {formatted_date}"
            else:
                subtitle = "Based on your body measurements and somatotype analysis"
        else:
            subtitle = "Based on your body measurements and somatotype analysis"
            
        story.append(Paragraph(subtitle, self.styles['CustomBodyText']))
        story.append(HRFlowable(width="100%", thickness=1, color=self.BRAND_PRIMARY))
    
    def _add_captured_images_section(self, story: List, record_data: Dict):
        """Add captured images section for history detail"""
        story.append(Paragraph("📸 Captured Images", self.styles['SectionHeader']))
        
        front_image_path = record_data.get('front_image_path')
        side_image_path = record_data.get('side_image_path')
        
        images_data = []
        if front_image_path and os.path.exists(front_image_path):
            images_data.append(["Front View", front_image_path])
        if side_image_path and os.path.exists(side_image_path):
            images_data.append(["Side View", side_image_path])
        
        if images_data:
            # Create table for images
            image_table_data = []
            image_row = []
            
            for label, image_path in images_data:
                try:
                    # Resize image to fit PDF
                    img = self._prepare_image_for_pdf(image_path, max_width=6*cm, max_height=8*cm)
                    if img:
                        cell_data = [
                            Paragraph(label, self.styles['CustomCaption']),
                            img
                        ]
                        image_row.append(cell_data)
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")
                    image_row.append([
                        Paragraph(label, self.styles['CustomCaption']),
                        Paragraph("Image not available", self.styles['CustomCaption'])
                    ])
            
            if image_row:
                # Create table with images side by side
                if len(image_row) == 2:
                    table_data = [
                        [image_row[0][1], image_row[1][1]],
                        [image_row[0][0], image_row[1][0]]
                    ]
                else:
                    table_data = [[image_row[0][1]], [image_row[0][0]]]
                
                image_table = Table(table_data, colWidths=[8*cm, 8*cm] if len(image_row) == 2 else [8*cm])
                image_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('BACKGROUND', (0, 1), (-1, 1), self.BRAND_SECONDARY)
                ]))
                story.append(image_table)
        else:
            story.append(Paragraph("Images not available for this analysis.", self.styles['CustomBodyText']))
    
    def _add_user_summary(self, story: List, record_data: Dict):
        """Add comprehensive user summary with all preferences"""
        name = record_data.get('name', 'Unknown User')
        gender = record_data.get('gender', 'Unknown')
        age = record_data.get('age', 'N/A')
        goal = record_data.get('goal', 'Not specified')
        
        # Add additional user preferences
        weight = record_data.get('weight', 'N/A')
        height = record_data.get('height', 'N/A')
        activity_level = record_data.get('activity_level', 'Not specified')
        dietary_restrictions = record_data.get('dietary_restrictions', 'None')
        exercise_preference = record_data.get('exercise_preference', 'Not specified')
        somatotype_class = record_data.get('somatotype_class', 'Not analyzed')
        
        story.append(Paragraph("👤 Complete Personal Profile", self.styles['SectionHeader']))
        
        # Split into two columns for better space usage
        basic_info_data = [
            ['Name:', name],
            ['Gender:', gender.title()],
            ['Age:', f"{age} years old" if age != 'N/A' else 'N/A'],
            ['Goal:', goal]
        ]
        
        profile_info_data = [
            ['Weight:', f"{weight} kg" if weight != 'N/A' else 'N/A'],
            ['Height:', f"{height} cm" if height != 'N/A' else 'N/A'],
            ['Activity Level:', activity_level],
            ['Body Type:', somatotype_class.title()]
        ]
        
        # Create side-by-side tables for better space efficiency
        combined_table_data = []
        max_rows = max(len(basic_info_data), len(profile_info_data))
        
        for i in range(max_rows):
            row = []
            if i < len(basic_info_data):
                row.extend(basic_info_data[i])
            else:
                row.extend(['', ''])
            if i < len(profile_info_data):
                row.extend(profile_info_data[i])
            else:
                row.extend(['', ''])
            combined_table_data.append(row)
        
        user_table = Table(combined_table_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.BRAND_SECONDARY),
            ('BACKGROUND', (2, 0), (2, -1), self.BRAND_SECONDARY),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_GRAY_DARK),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(user_table)
        
        # Add preferences section if available
        if dietary_restrictions != 'None' or exercise_preference != 'Not specified':
            story.append(Spacer(1, 10))
            story.append(Paragraph("🎯 Personal Preferences", self.styles['SubsectionHeader']))
            
            preferences_data = []
            if dietary_restrictions != 'None':
                preferences_data.append(['Dietary Restrictions:', dietary_restrictions])
            if exercise_preference != 'Not specified':
                preferences_data.append(['Exercise Preference:', exercise_preference])
            
            if preferences_data:
                pref_table = Table(preferences_data, colWidths=[4*cm, 8*cm])
                pref_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), self.BRAND_SECONDARY),
                    ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_GRAY_DARK),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(pref_table)
    
    def _add_nutrition_section(self, story: List, record_data: Dict):
        """Add nutrition analysis section"""
        story.append(Paragraph("🍽️ Nutritional Analysis", self.styles['SectionHeader']))
        
        # Calorie information
        calories = record_data.get('calories', 2000)
        goal = record_data.get('goal', 'Maintain Weight')
        
        calorie_text = f"<b>Daily Caloric Target:</b> {calories} calories<br/><b>Goal:</b> {goal}"
        story.append(Paragraph(calorie_text, self.styles['HighlightBox']))
        story.append(Spacer(1, 15))
        
        # Macronutrient chart
        self._add_macronutrient_chart(story, record_data)
    
    def _add_macronutrient_chart(self, story: List, record_data: Dict):
        """Add macronutrient distribution chart"""
        # Default values
        protein_pct = 30
        carbs_pct = 45  
        fat_pct = 25
        
        # Try to get actual values from diet data
        session_id = record_data.get('session_id')
        if session_id:
            try:
                from utils.database import DatabaseManager
                db_manager = DatabaseManager()
                diet_data = db_manager.get_diet_recommendations(session_id)
                
                if diet_data:
                    nutrition_data = diet_data.get('nutrition_data', {})
                    protein_pct = int(nutrition_data.get('protein_percentage', 30))
                    carbs_pct = int(nutrition_data.get('carbs_percentage', 45))
                    fat_pct = int(nutrition_data.get('fat_percentage', 25))
            except Exception as e:
                print(f"Could not load nutrition data: {e}")
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        
        sizes = [protein_pct, carbs_pct, fat_pct]
        labels = [f'Protein ({protein_pct}%)', f'Carbs ({carbs_pct}%)', f'Fat ({fat_pct}%)']
        colors = ['#28A745', '#FFC107', '#2E5266']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 12})
        
        ax.set_title('Daily Macronutrient Distribution', fontsize=16, fontweight='bold', pad=20)
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        # Add to story
        img = Image(img_buffer, width=12*cm, height=9*cm)
        story.append(img)
        story.append(Spacer(1, 10))
    
    def _add_somatotype_section(self, story: List, record_data: Dict):
        """Add somatotype analysis section"""
        story.append(Paragraph("🏃 Body Type Analysis", self.styles['SectionHeader']))
        
        # Get somatotype data
        ectomorph = 33
        mesomorph = 33
        endomorph = 34
        somatotype_class = "Balanced"
        
        session_id = record_data.get('session_id')
        if session_id:
            try:
                from utils.database import DatabaseManager
                db_manager = DatabaseManager()
                soma_data = db_manager.get_somatotype_classification(session_id)
                
                if soma_data:
                    ectomorph = float(soma_data.get('ectomorph', 33))
                    mesomorph = float(soma_data.get('mesomorph', 33))
                    endomorph = float(soma_data.get('endomorph', 34))
                    somatotype_class = soma_data.get('somatotype_class', 'Balanced')
            except Exception as e:
                print(f"Could not load somatotype data: {e}")
        
        # Classification
        classification_text = f"<b>Your Body Type Classification:</b> {somatotype_class}"
        story.append(Paragraph(classification_text, self.styles['HighlightBox']))
        story.append(Spacer(1, 15))
        
        # Somatotype scores table
        soma_data = [
            ['Body Type', 'Score (%)', 'Description'],
            ['Ectomorph', f'{ectomorph:.1f}%', 'Lean & tall body type, fast metabolism'],
            ['Mesomorph', f'{mesomorph:.1f}%', 'Athletic & muscular, responds quickly to exercise'],
            ['Endomorph', f'{endomorph:.1f}%', 'Soft & round body type, slower metabolism']
        ]
        
        soma_table = Table(soma_data, colWidths=[4*cm, 3*cm, 8*cm])
        soma_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.BRAND_GRAY_LIGHT)
        ]))
        story.append(soma_table)
    
    def _add_diet_recommendations(self, story: List, record_data: Dict):
        """Add comprehensive diet recommendations section - copy GUI approach exactly"""
        story.append(Paragraph("🥗 Diet Recommendations", self.styles['SectionHeader']))
        
        try:
            # Load data exactly like GUI - database first, then local files
            session_id = record_data.get('session_id')
            meal_data = None
            
            if session_id:
                # Try database first (same as GUI)
                diet_data = self.db_manager.get_diet_recommendations(session_id)
                if diet_data and 'meal_recommendations' in diet_data:
                    meal_recommendations_raw = diet_data['meal_recommendations']
                    
                    # Parse JSON if needed (exact GUI logic)
                    if isinstance(meal_recommendations_raw, str):
                        try:
                            meal_data = json.loads(meal_recommendations_raw)
                            print("DEBUG - PDF: Successfully parsed meal recommendations from database")
                        except json.JSONDecodeError:
                            print("ERROR - PDF: Failed to parse meal recommendations JSON")
                            meal_data = None
                    else:
                        meal_data = meal_recommendations_raw
                        
                    # Check if meal data has proper structure
                    if meal_data:
                        if 'meals' in meal_data:
                            meals = meal_data['meals']
                            print(f"DEBUG - PDF: Found meals structure with keys: {list(meals.keys())}")
                            self._add_meals_from_gui_format(story, meals)
                            return
                        elif any(key in meal_data for key in ['breakfast', 'lunch', 'dinner', 'snack']):
                            print("DEBUG - PDF: Found direct meal structure")
                            self._add_meals_from_gui_format(story, meal_data)
                            return
                        else:
                            print("DEBUG - PDF: No recognized meal structure found in database")
            
            # No database data, use local CSV files like GUI does
            print("DEBUG - PDF: Loading from CSV templates like GUI")
            self._add_csv_based_recommendations(story, record_data)
            
        except Exception as e:
            print(f"Error loading diet recommendations: {e}")
            import traceback
            traceback.print_exc()
            # Final fallback
            self._add_fallback_diet_recommendations(story, record_data)

    def _add_meals_from_gui_format(self, story: List, meals: Dict):
        """Add meal recommendations using exact GUI format and data loading"""
        try:
            # Add diet principles first (similar to GUI layout)
            story.append(Paragraph("Nutritional Guidelines", self.styles['SubsectionHeader']))
            story.append(Paragraph("• Follow balanced portions for each meal", self.styles['BodyText']))
            story.append(Paragraph("• Include protein, carbohydrates, and healthy fats", self.styles['BodyText']))
            story.append(Paragraph("• Stay hydrated throughout the day", self.styles['BodyText']))
            story.append(Spacer(1, 15))
            
            # Process meals exactly like GUI MealBasedFoodRecommendations
            meal_order = ['breakfast', 'lunch', 'dinner', 'snack']
            
            for meal_type in meal_order:
                if meal_type in meals:
                    meal_data = meals[meal_type]
                    
                    # Handle different data structures (copying GUI logic)
                    foods = []
                    if isinstance(meal_data, list):
                        foods = meal_data
                    elif isinstance(meal_data, dict):
                        foods = meal_data.get('foods', [])
                    elif isinstance(meal_data, str):
                        foods = [meal_data]
                    
                    if foods:
                        self._add_meal_category_section(story, meal_type, foods)
                        
        except Exception as e:
            print(f"Error adding meals from GUI format: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_meal_category_section(self, story: List, meal_type: str, foods: List):
        """Add a meal category section with food details (copying GUI FoodCard approach)"""
        try:
            # Meal category header with icons (matching GUI)
            meal_icons = {
                'breakfast': '🌅',
                'lunch': '🌞', 
                'dinner': '🌙',
                'snack': '🍎'
            }
            icon = meal_icons.get(meal_type.lower(), '🍽️')
            
            story.append(Paragraph(f"{icon} {meal_type.title()}", self.styles['SubsectionHeader']))
            
            # Process foods like GUI FoodCard class
            foods_to_show = foods[:6] if isinstance(foods, list) else [foods]  # Limit to 6 foods
            
            # Create table for better layout
            food_table_data = []
            current_row = []
            
            for i, food_data in enumerate(foods_to_show):
                # Extract food information (copying GUI FoodCard logic exactly)
                food_name = "Unknown Food"
                calories = 0
                protein = 0
                
                if isinstance(food_data, dict):
                    # Try to get complete food data using food_loader like GUI does
                    food_name = food_data.get('Food_Item', food_data.get('name', 'Unknown Food'))
                    if food_name and food_name != 'Unknown Food':
                        # Use food_loader exactly like GUI FoodCard
                        complete_food_data = self.food_loader.get_food_info(food_name)
                        if complete_food_data:
                            food_name = complete_food_data['Food_Item']
                            calories = float(complete_food_data.get('Calories_kcal', 0))
                            protein = float(complete_food_data.get('Protein_g', 0))
                        else:
                            calories = food_data.get('Calories_kcal', 0)
                            protein = food_data.get('Protein_g', 0)
                    else:
                        food_name = food_data.get('Food_Item', 'Unknown Food')
                        calories = food_data.get('Calories_kcal', 0)
                        protein = food_data.get('Protein_g', 0)
                elif isinstance(food_data, str) and food_data.strip():
                    # Handle string input like GUI FoodCard
                    complete_food_data = self.food_loader.get_food_info(food_data.strip())
                    if complete_food_data:
                        food_name = complete_food_data['Food_Item']
                        calories = float(complete_food_data.get('Calories_kcal', 0))
                        protein = float(complete_food_data.get('Protein_g', 0))
                    else:
                        food_name = str(food_data).strip()
                        calories = 0
                        protein = 0
                else:
                    food_name = str(food_data)
                    calories = 0
                    protein = 0
                
                # Format food info (matching GUI display)
                food_text = f"<b>{food_name}</b><br/>"
                if calories > 0:
                    food_text += f"Calories: {calories:.0f} kcal<br/>"
                if protein > 0:
                    food_text += f"Protein: {protein:.1f}g"
                
                current_row.append(Paragraph(food_text, self.styles['BodyText']))
                
                # Create row every 2 foods for better layout
                if len(current_row) == 2 or i == len(foods_to_show) - 1:
                    # Pad row if needed
                    while len(current_row) < 2:
                        current_row.append("")
                    food_table_data.append(current_row)
                    current_row = []
            
            if food_table_data:
                # Create table with food information
                food_table = Table(food_table_data, colWidths=[8*cm, 8*cm])
                food_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(food_table)
                story.append(Spacer(1, 15))
            
        except Exception as e:
            print(f"Error adding meal category section: {e}")
            import traceback
            traceback.print_exc()

    def _add_csv_based_recommendations(self, story: List, record_data: Dict):
        """Load diet recommendations from CSV templates (copying GUI approach)"""
        try:
            # Load diet templates CSV
            diet_templates_path = os.path.join(PROJECT_DIR, "diet_templates.csv")
            if not os.path.exists(diet_templates_path):
                self._add_fallback_diet_recommendations(story, record_data)
                return
                
            import pandas as pd
            templates_df = pd.read_csv(diet_templates_path)
            
            # Get user info for matching template
            somatotype_class = record_data.get('somatotype_class', 'mesomorph').lower()
            goal = record_data.get('goal', 'weight_loss').lower().replace(' ', '_')
            
            # Try to find matching template
            matching_template = templates_df[
                (templates_df['somatotype'].str.lower() == somatotype_class) &
                (templates_df['goal'].str.lower() == goal)
            ]
            
            if matching_template.empty:
                # Try fallback with just somatotype
                matching_template = templates_df[
                    templates_df['somatotype'].str.lower() == somatotype_class
                ]
            
            if matching_template.empty:
                # Use first available template
                matching_template = templates_df.head(1)
            
            template = matching_template.iloc[0]
            
            # Extract nutritional information
            protein_g = int(template.get('protein_g', 130))
            carbs_g = int(template.get('carbs_g', 200))
            fats_g = int(template.get('fats_g', 60))
            
            # Parse foods list
            foods_list = str(template.get('foods', '')).split(', ')
            
            # Add sections matching GUI layout
            self._add_diet_principles_section_csv(story, somatotype_class, goal)
            story.append(Spacer(1, 15))
            
            self._add_fitness_strategy_section_csv(story, somatotype_class)  
            story.append(Spacer(1, 15))
            
            # Add meal recommendations by category
            self._add_meal_recommendations_by_category(story, foods_list, protein_g, carbs_g, fats_g)
            
        except Exception as e:
            print(f"Error loading CSV-based recommendations: {e}")
            self._add_fallback_diet_recommendations(story, record_data)

    def _add_diet_principles_section(self, story: List, diet_data: Dict):
        """Add diet principles section"""
        story.append(Paragraph("Nutritional Guidelines", self.styles['SubsectionHeader']))
        
        # Get diet principles from database
        diet_principles_raw = diet_data.get('diet_principles', '[]')
        
        try:
            if isinstance(diet_principles_raw, str):
                import json
                diet_principles = json.loads(diet_principles_raw)
            else:
                diet_principles = diet_principles_raw
        except:
            diet_principles = []
        
        # Default principles if none found
        if not diet_principles:
            diet_principles = [
                "Focus on whole, minimally processed foods",
                "Maintain consistent meal timing throughout the day", 
                "Stay adequately hydrated with 8-10 glasses of water daily",
                "Include a variety of colorful fruits and vegetables",
                "Choose lean protein sources for muscle maintenance",
                "Control portion sizes based on your goals",
                "Limit refined sugars and processed snacks"
            ]
        
        # Display principles as bullet points
        for principle in diet_principles[:8]:  # Limit to 8 principles
            story.append(Paragraph(f"• {principle}", self.styles['CustomBodyText']))
        
    def _add_fitness_strategy_section(self, story: List, diet_data: Dict):
        """Add fitness strategy section"""
        story.append(Paragraph("Training Strategy", self.styles['SubsectionHeader']))
        
        # Get fitness strategy from database
        fitness_strategy_raw = diet_data.get('fitness_strategy', '{}')
        
        try:
            if isinstance(fitness_strategy_raw, str):
                import json
                fitness_strategy = json.loads(fitness_strategy_raw)
            else:
                fitness_strategy = fitness_strategy_raw
        except:
            fitness_strategy = {}
        
        # Default strategy if none found
        if not fitness_strategy:
            fitness_strategy = {
                'strength_days': 3,
                'cardio_days': 2,
                'rest_days': 2,
                'focus': 'Balanced training approach'
            }
        
        # Display strategy information
        strength_days = fitness_strategy.get('strength_days', 3)
        cardio_days = fitness_strategy.get('cardio_days', 2)
        rest_days = fitness_strategy.get('rest_days', 2)
        focus = fitness_strategy.get('focus', 'Balanced training approach')
        
        strategy_text = f"""
        <b>Weekly Training Split:</b><br/>
        • Strength Training: {strength_days} days per week<br/>
        • Cardiovascular Exercise: {cardio_days} days per week<br/>
        • Rest Days: {rest_days} days per week<br/>
        • Focus: {focus}
        """
        story.append(Paragraph(strategy_text, self.styles['CustomBodyText']))
        
    def _add_meal_recommendations_section(self, story: List, diet_data: Dict):
        """Add meal-based food recommendations section"""
        story.append(Paragraph("Recommended Foods by Meal", self.styles['SubsectionHeader']))
        
        # Get meal recommendations from database
        meal_recommendations_raw = diet_data.get('meal_recommendations', '{}')
        
        try:
            if isinstance(meal_recommendations_raw, str):
                import json
                meal_recommendations = json.loads(meal_recommendations_raw)
            else:
                meal_recommendations = meal_recommendations_raw
        except:
            meal_recommendations = {}
        
        if not meal_recommendations:
            story.append(Paragraph("Meal recommendations will be customized based on your specific dietary preferences and goals.", self.styles['CustomBodyText']))
            return
        
        # Define meal order and icons
        meal_order = ['breakfast', 'lunch', 'dinner', 'snack']
        meal_icons = {
            'breakfast': '🌅',
            'lunch': '🌞', 
            'dinner': '🌙',
            'snack': '🍎'
        }
        
        for meal_type in meal_order:
            meal_data = meal_recommendations.get(meal_type, [])
            if not meal_data:
                continue
                
            # Handle different data structures
            foods = []
            if isinstance(meal_data, list):
                foods = meal_data
            elif isinstance(meal_data, dict):
                foods = meal_data.get('foods', [])
            elif isinstance(meal_data, str):
                foods = [meal_data]
            
            if not foods:
                continue
                
            # Meal header
            icon = meal_icons.get(meal_type.lower(), '🍽️')
            story.append(Paragraph(f"{icon} {meal_type.title()}", self.styles['SubsectionHeader']))
            
            # Create table for foods with nutritional info
            food_table_data = [['Food', 'Calories (per serving)', 'Key Benefits']]
            
            # Show top 6 foods for each meal
            foods_to_show = foods[:6] if isinstance(foods, list) else [foods]
            
            for food in foods_to_show:
                if isinstance(food, dict):
                    food_name = food.get('name', food.get('food_name', 'Unknown Food'))
                    calories = food.get('calories', food.get('calories_per_serving', 'N/A'))
                    benefits = food.get('nutritional_benefits', food.get('benefits', 'Good nutrition'))
                    
                    # Truncate long names and benefits
                    if len(food_name) > 25:
                        food_name = food_name[:22] + "..."
                    if len(str(benefits)) > 40:
                        benefits = str(benefits)[:37] + "..."
                        
                    food_table_data.append([
                        food_name,
                        f"{calories}" if calories != 'N/A' else 'N/A',
                        str(benefits)
                    ])
                else:
                    # Simple string format
                    food_name = str(food)
                    if len(food_name) > 25:
                        food_name = food_name[:22] + "..."
                    food_table_data.append([food_name, 'N/A', 'Nutritious choice'])
            
            # Create and style the food table
            if len(food_table_data) > 1:  # Has data beyond header
                food_table = Table(food_table_data, colWidths=[6*cm, 4*cm, 6*cm])
                food_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_GRAY_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Food names left-aligned
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Calories centered
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),   # Benefits left-aligned
                    
                    # Grid and padding
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    
                    # Alternating row colors for better readability
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_SECONDARY])
                ]))
                story.append(food_table)
            else:
                story.append(Paragraph(f"No specific recommendations available for {meal_type}.", self.styles['CustomBodyText']))
            
            story.append(Spacer(1, 10))
    
    def _add_diet_principles_section_csv(self, story: List, somatotype_class: str, goal: str):
        """Add diet principles section based on somatotype and goal"""
        story.append(Paragraph("Nutritional Guidelines", self.styles['SubsectionHeader']))
        
        # Somatotype-specific diet principles
        principles = {
            'ectomorph': [
                "Eat frequently with smaller, frequent meals throughout the day",
                "Focus on complex carbohydrates for sustained energy",
                "Include healthy fats to support weight gain and hormone production", 
                "Don't skip meals - consistency is key for weight management",
                "Stay hydrated but avoid filling up on liquids before meals",
                "Include post-workout meals within 30 minutes of exercise"
            ],
            'mesomorph': [
                "Balance macronutrients with moderate portions",
                "Time carbohydrate intake around workouts for optimal performance",
                "Focus on high-quality protein sources for muscle maintenance",
                "Include a variety of nutrients from different food sources",
                "Practice portion control to maintain healthy body composition",
                "Stay consistent with meal timing for metabolic efficiency"
            ],
            'endomorph': [
                "Focus on protein and healthy fats while limiting simple carbs",
                "Eat smaller, more frequent meals to boost metabolism",
                "Choose low-glycemic foods to manage blood sugar levels", 
                "Include fiber-rich foods to promote satiety and digestion",
                "Stay hydrated to support metabolic processes",
                "Avoid late-night eating to optimize fat burning during sleep"
            ]
        }
        
        # Get principles for this somatotype or use mesomorph as default
        soma_principles = principles.get(somatotype_class, principles['mesomorph'])
        
        # Goal-specific adjustments
        if 'weight_gain' in goal.lower() or 'gain' in goal.lower():
            soma_principles = soma_principles + [
                "Increase overall caloric intake with nutrient-dense foods",
                "Add healthy snacks between main meals"
            ]
        elif 'weight_loss' in goal.lower() or 'loss' in goal.lower():
            soma_principles = soma_principles + [
                "Create a moderate caloric deficit through portion control",
                "Focus on high-satiety foods to manage hunger"
            ]
        
        # Display principles
        for principle in soma_principles[:6]:  # Limit to 6 principles
            story.append(Paragraph(f"• {principle}", self.styles['CustomBodyText']))
    
    def _add_fitness_strategy_section_csv(self, story: List, somatotype_class: str):
        """Add fitness strategy section based on somatotype"""  
        story.append(Paragraph("Training Strategy", self.styles['SubsectionHeader']))
        
        # Somatotype-specific fitness strategies
        strategies = {
            'ectomorph': {
                'strength_days': 4,
                'cardio_days': 2, 
                'focus': 'Strength training with compound movements for mass building',
                'strategy': 'Focus on progressive overload and adequate rest'
            },
            'mesomorph': {
                'strength_days': 3,
                'cardio_days': 3,
                'focus': 'Balanced training combining strength and cardiovascular fitness',
                'strategy': 'Mix of compound and isolation exercises'
            },
            'endomorph': {
                'strength_days': 3,
                'cardio_days': 4,
                'focus': 'Higher intensity cardio with strength training for fat loss',
                'strategy': 'Circuit training and HIIT for metabolic boost'
            }
        }
        
        strategy = strategies.get(somatotype_class, strategies['mesomorph'])
        
        strength_days = strategy['strength_days']
        cardio_days = strategy['cardio_days']
        rest_days = 7 - strength_days - cardio_days if strength_days + cardio_days <= 7 else 1
        focus = strategy['focus']
        
        strategy_text = f"""
        <b>Weekly Training Split:</b><br/>
        • Strength Training: {strength_days} days per week<br/>
        • Cardiovascular Exercise: {cardio_days} days per week<br/>
        • Rest Days: {rest_days} days per week<br/>
        • Focus: {focus}
        """
        story.append(Paragraph(strategy_text, self.styles['CustomBodyText']))
    
    def _add_meal_recommendations_by_category(self, story: List, foods_list: List, protein_g: int, carbs_g: int, fats_g: int):
        """Add meal recommendations organized by meal category using food data loader"""
        story.append(Paragraph("Recommended Foods by Meal", self.styles['SubsectionHeader']))
        
        # Categorize foods by meal timing using food data loader
        meal_categories = {
            'breakfast': [],
            'lunch': [],
            'dinner': [], 
            'snack': []
        }
        
        # Process foods and get detailed info
        for food_name in foods_list:
            if not food_name or not food_name.strip():
                continue
                
            # Get detailed food info from our food database
            food_info = self.food_loader.get_food_info(food_name.strip())
            
            if food_info:
                # Use timing info from database
                meal_timing = food_info.get('Meal_Timing', 'any time').lower()
                
                # Map timing to our categories
                if 'breakfast' in meal_timing or 'morning' in meal_timing:
                    meal_categories['breakfast'].append(food_info)
                elif 'lunch' in meal_timing or 'midday' in meal_timing:
                    meal_categories['lunch'].append(food_info)  
                elif 'dinner' in meal_timing or 'evening' in meal_timing:
                    meal_categories['dinner'].append(food_info)
                elif 'snack' in meal_timing:
                    meal_categories['snack'].append(food_info)
                else:
                    # Distribute across all meals if timing is "any time"
                    meal_categories['breakfast'].append(food_info)
                    meal_categories['lunch'].append(food_info)
                    meal_categories['dinner'].append(food_info)
                    if len(meal_categories['snack']) < 3:  # Limit snacks
                        meal_categories['snack'].append(food_info)
            else:
                # Fallback if food not found in database
                fallback_info = {
                    'Food_Item': food_name.strip(),
                    'Calories_kcal': 'N/A',
                    'Enhanced_Category': 'General',
                    'Overall_Quality': 'Good choice'
                }
                # Add to all meal categories as fallback
                for category in meal_categories:
                    meal_categories[category].append(fallback_info)
        
        # Display meals with icons
        meal_icons = {
            'breakfast': '🌅',
            'lunch': '🌞',
            'dinner': '🌙', 
            'snack': '🍎'
        }
        
        for meal_type, foods in meal_categories.items():
            if not foods:
                continue
                
            icon = meal_icons.get(meal_type, '🍽️')
            story.append(Paragraph(f"{icon} {meal_type.title()}", self.styles['SubsectionHeader']))
            
            # Create detailed food table
            food_table_data = [['Food', 'Calories (per 100g)', 'Category', 'Quality']]
            
            # Show up to 4 foods per meal to avoid clutter
            foods_to_show = foods[:4]
            
            for food_info in foods_to_show:
                food_name = food_info.get('Food_Item', 'Unknown Food')
                calories = food_info.get('Calories_kcal', 'N/A')
                category = food_info.get('Enhanced_Category', 'General')
                quality = food_info.get('Overall_Quality', 'Good')
                
                # Format values
                if isinstance(calories, (int, float)) and calories > 0:
                    calories_str = f"{int(calories)}"
                else:
                    calories_str = "N/A"
                
                # Truncate long values
                if len(food_name) > 20:
                    food_name = food_name[:17] + "..."
                if len(category) > 15:
                    category = category[:12] + "..."
                if len(quality) > 15:
                    quality = quality[:12] + "..."
                
                food_table_data.append([food_name, calories_str, category, quality])
            
            # Create and style table
            if len(food_table_data) > 1:
                food_table = Table(food_table_data, colWidths=[5*cm, 3*cm, 4*cm, 4*cm])
                food_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Data rows
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_GRAY_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Food names left
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Calories center
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Category left
                    ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Quality left
                    
                    # Grid and padding
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    
                    # Alternating colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_SECONDARY])
                ]))
                story.append(food_table)
            
            story.append(Spacer(1, 12))
        
        # Add macronutrient summary
        story.append(Paragraph("Daily Nutritional Targets", self.styles['SubsectionHeader']))
        macro_text = f"""
        <b>Recommended Daily Intake:</b><br/>
        • Protein: {protein_g}g per day<br/>
        • Carbohydrates: {carbs_g}g per day<br/>
        • Fats: {fats_g}g per day<br/>
        • Total Calories: Approximately {int(protein_g * 4 + carbs_g * 4 + fats_g * 9)} calories
        """
        story.append(Paragraph(macro_text, self.styles['CustomBodyText']))
    
    def _add_fallback_diet_recommendations(self, story: List, record_data: Dict):
        """Add basic fallback diet recommendations when data is unavailable"""
        story.append(Paragraph("General Nutritional Guidelines", self.styles['SubsectionHeader']))
        
        general_principles = [
            "Focus on whole, unprocessed foods for optimal nutrition",
            "Include lean protein sources with every meal",
            "Eat a variety of colorful fruits and vegetables daily", 
            "Stay hydrated with 8-10 glasses of water per day",
            "Control portion sizes based on your individual goals",
            "Time your meals consistently throughout the day"
        ]
        
        for principle in general_principles:
            story.append(Paragraph(f"• {principle}", self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("For personalized recommendations, please complete a full dietary analysis.", self.styles['CustomBodyText']))

    def _add_exercise_recommendations(self, story: List, record_data: Dict):
        """Add comprehensive exercise recommendations - copy GUI approach exactly"""
        story.append(PageBreak())
        story.append(Paragraph("💪 Exercise Recommendations", self.styles['SectionHeader']))
        
        try:
            # Load data exactly like GUI - database first, then local files
            session_id = record_data.get('session_id')
            exercise_data = None
            fitness_data = None
            
            if session_id:
                # Try database first (same as GUI)
                diet_data = self.db_manager.get_diet_recommendations(session_id)
                fitness_data = self.db_manager.get_fitness_recommendations(session_id)
                
                # Extract exercise data like GUI does
                if diet_data and 'meal_recommendations' in diet_data:
                    meal_recommendations_raw = diet_data['meal_recommendations']
                    if isinstance(meal_recommendations_raw, str):
                        try:
                            meal_data = json.loads(meal_recommendations_raw)
                            if 'exercises' in meal_data:
                                exercise_data = meal_data['exercises']
                                print(f"DEBUG - PDF: Found exercise data in meal data")
                        except json.JSONDecodeError:
                            pass
                
                # Use fitness data if no exercises in meal data (GUI logic)
                if not exercise_data and fitness_data and fitness_data.get('exercises'):
                    exercise_data = fitness_data['exercises']
                    print(f"DEBUG - PDF: Found exercise data in fitness data")
            
            if exercise_data:
                # Use database exercise data (copy GUI ExerciseRecommendations)
                self._add_exercises_from_gui_format(story, exercise_data, record_data)
            else:
                # No database data, use local JSON files like GUI does
                print("DEBUG - PDF: Loading from JSON files like GUI")
                self._add_json_based_exercise_recommendations(story, record_data)
                
        except Exception as e:
            print(f"Error loading exercise recommendations: {e}")
            import traceback
            traceback.print_exc()
            # Final fallback
            self._add_fallback_exercise_recommendations(story, record_data)

    def _add_exercises_from_gui_format(self, story: List, exercise_data: Dict, record_data: Dict):
        """Add exercise recommendations using exact GUI format (copying ExerciseRecommendations class)"""
        try:
            # Extract exercise info (copying GUI logic exactly)
            exercise_type = exercise_data.get('exercise_type', 'bodyweight')
            exercise_complexity = exercise_data.get('exercise_complexity', 'beginner')
            workout_description = exercise_data.get('workout_description', f'{exercise_type} {exercise_complexity} workout')
            
            # Header section (matching GUI)
            header_text = f"🏋️ <b>{exercise_type.title()}</b> | 📊 <b>{exercise_complexity.title()}</b>"
            story.append(Paragraph(header_text, self.styles['BodyText']))
            story.append(Spacer(1, 10))
            
            # Workout description
            story.append(Paragraph(workout_description, self.styles['CustomBodyText']))
            story.append(Spacer(1, 15))
            
            # Schedule info (matching GUI)
            strength_days = exercise_data.get('strength_days', 0)
            cardio_days = exercise_data.get('cardio_days', 0)
            
            schedule_text = f"<b>Weekly Schedule:</b> 💪 Strength: {strength_days} days/week | ❤️ Cardio: {cardio_days} days/week"
            story.append(Paragraph(schedule_text, self.styles['CustomBodyText']))
            story.append(Spacer(1, 15))
            
            # Exercise lists (copying GUI logic exactly)
            if exercise_type == 'gym':
                self._add_gym_exercises_gui_format(story, exercise_data)
            else:
                self._add_bodyweight_exercises_gui_format(story, exercise_data)
                
        except Exception as e:
            print(f"Error adding exercises from GUI format: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_gym_exercises_gui_format(self, story: List, exercise_data: Dict):
        """Create gym exercise display with push/pull/legs split (copying GUI)"""
        try:
            story.append(Paragraph("Exercise Categories", self.styles['SubsectionHeader']))
            
            # Create table for push/pull/legs layout
            exercise_table_data = []
            headers = ["🔥 Push", "⬇️ Pull", "🦵 Legs"]
            exercise_table_data.append(headers)
            
            # Get exercises (copying GUI limits)
            push_exercises = exercise_data.get('push_exercises', [])[:4]
            pull_exercises = exercise_data.get('pull_exercises', [])[:4]
            legs_exercises = exercise_data.get('legs_exercises', [])[:4]
            
            # Process exercises like GUI does
            push_processed = self._process_exercise_list(push_exercises)
            pull_processed = self._process_exercise_list(pull_exercises)
            legs_processed = self._process_exercise_list(legs_exercises)
            
            # Create rows
            max_exercises = max(len(push_processed), len(pull_processed), len(legs_processed))
            for i in range(max_exercises):
                row = []
                row.append(push_processed[i] if i < len(push_processed) else "")
                row.append(pull_processed[i] if i < len(pull_processed) else "")
                row.append(legs_processed[i] if i < len(legs_processed) else "")
                exercise_table_data.append(row)
            
            if len(exercise_table_data) > 1:  # Has data beyond headers
                exercise_table = Table(exercise_table_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
                exercise_table.setStyle(TableStyle([
                    # Header style
                    ('BACKGROUND', (0,0), (-1,0), self.BRAND_PRIMARY),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 12),
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    
                    # Data style
                    ('TEXTCOLOR', (0,1), (-1,-1), self.BRAND_GRAY_DARK),
                    ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                    ('FONTSIZE', (0,1), (-1,-1), 9),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    
                    # Grid and padding
                    ('GRID', (0,0), (-1,-1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(exercise_table)
                story.append(Spacer(1, 15))
            
        except Exception as e:
            print(f"Error adding gym exercises: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_bodyweight_exercises_gui_format(self, story: List, exercise_data: Dict):
        """Create bodyweight exercise display (copying GUI)"""
        try:
            story.append(Paragraph("🏃 Bodyweight Exercises", self.styles['SubsectionHeader']))
            
            bodyweight_exercises = exercise_data.get('bodyweight_exercises', [])[:8]
            processed_exercises = self._process_exercise_list(bodyweight_exercises)
            
            if processed_exercises:
                # Create 2-column layout for better space usage
                exercise_table_data = []
                for i in range(0, len(processed_exercises), 2):
                    row = []
                    row.append(processed_exercises[i])
                    row.append(processed_exercises[i+1] if i+1 < len(processed_exercises) else "")
                    exercise_table_data.append(row)
                
                if exercise_table_data:
                    exercise_table = Table(exercise_table_data, colWidths=[8*cm, 8*cm])
                    exercise_table.setStyle(TableStyle([
                        ('TEXTCOLOR', (0,0), (-1,-1), self.BRAND_GRAY_DARK),
                        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                        ('FONTSIZE', (0,0), (-1,-1), 10),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 6),
                        ('RIGHTPADDING', (0,0), (-1,-1), 6),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ]))
                    story.append(exercise_table)
                    story.append(Spacer(1, 15))
            
        except Exception as e:
            print(f"Error adding bodyweight exercises: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_exercise_list(self, exercises: List) -> List[str]:
        """Process exercise list using exercise_loader like GUI does"""
        processed = []
        for exercise in exercises:
            if exercise and str(exercise).strip():
                exercise_str = str(exercise).strip()
                
                # Try to get exercise name from loader (copying GUI logic)
                exercise_info = self.exercise_loader.get_exercise_info(exercise_str)
                
                if exercise_info:
                    # Found exercise in database, use proper name
                    exercise_name = exercise_info['name'].title()
                else:
                    # Not found in database or already a name, use as is
                    exercise_name = exercise_str.title()
                
                processed.append(f"• {exercise_name}")
        
        return processed
    
    def _add_json_based_exercise_recommendations(self, story: List, record_data: Dict):
        """Load exercise recommendations from JSON files (copying GUI approach)"""
        try:
            # Get somatotype for exercise selection
            somatotype_class = record_data.get('somatotype_class', 'mesomorph').lower()
            goal = record_data.get('goal', 'weight_loss').lower()
            
            # Add training strategy section
            self._add_training_strategy_csv(story, somatotype_class)
            story.append(Spacer(1, 15))
            
            # Get exercises from JSON based on somatotype and goals
            self._add_somatotype_exercises(story, somatotype_class, goal)
            
        except Exception as e:
            print(f"Error loading JSON-based exercises: {e}")
            self._add_fallback_exercise_recommendations(story, record_data)
    
    def _add_training_strategy_csv(self, story: List, somatotype_class: str):
        """Add training strategy based on somatotype"""  
        story.append(Paragraph("Training Strategy", self.styles['SubsectionHeader']))
        
        # Somatotype-specific training strategies
        strategies = {
            'ectomorph': {
                'strength_days': 4,
                'cardio_days': 2,
                'rest_days': 1,
                'focus': 'Strength training with compound movements for mass building',
                'approach': 'Heavy lifting with progressive overload'
            },
            'mesomorph': {
                'strength_days': 3,
                'cardio_days': 3,  
                'rest_days': 1,
                'focus': 'Balanced training combining strength and cardiovascular fitness',
                'approach': 'Mix of compound and isolation exercises'
            },
            'endomorph': {
                'strength_days': 3,
                'cardio_days': 4,
                'rest_days': 0,
                'focus': 'High-intensity training for fat loss and metabolic boost',
                'approach': 'Circuit training and HIIT protocols'
            }
        }
        
        strategy = strategies.get(somatotype_class, strategies['mesomorph'])
        
        strategy_text = f"""
        <b>Weekly Training Split:</b><br/>
        • Strength Training: {strategy['strength_days']} days per week<br/>
        • Cardiovascular Exercise: {strategy['cardio_days']} days per week<br/>
        • Rest Days: {strategy['rest_days']} days per week<br/>
        • Focus: {strategy['focus']}<br/>
        • Approach: {strategy['approach']}
        """
        story.append(Paragraph(strategy_text, self.styles['CustomBodyText']))
    
    def _add_somatotype_exercises(self, story: List, somatotype_class: str, goal: str):
        """Add exercises based on somatotype using exercise data loader"""
        story.append(Paragraph("Recommended Exercise Program", self.styles['SubsectionHeader']))
        
        # Define exercise categories based on somatotype and goal
        if somatotype_class == 'ectomorph':
            # Focus on compound movements and muscle building
            self._add_ectomorph_exercises(story, goal)
        elif somatotype_class == 'endomorph':
            # Focus on fat burning and metabolic exercises  
            self._add_endomorph_exercises(story, goal)
        else:  # mesomorph or default
            # Balanced approach
            self._add_mesomorph_exercises(story, goal)
    
    def _add_ectomorph_exercises(self, story: List, goal: str):
        """Add ectomorph-specific exercises focusing on mass building"""
        
        # Define exercise categories for ectomorphs
        exercise_categories = {
            'Upper Body Strength': ['barbell bench press', 'pull-up', 'barbell row', 'dumbbell shoulder press'],
            'Lower Body Power': ['barbell squat', 'deadlift', 'bulgarian split squat', 'walking lunge'],
            'Compound Movements': ['clean and press', 'thruster', 'barbell front squat', 'push-up']
        }
        
        self._render_exercise_categories(story, exercise_categories)
    
    def _add_mesomorph_exercises(self, story: List, goal: str):
        """Add mesomorph-specific exercises with balanced approach"""
        
        if 'loss' in goal.lower():
            # Focus more on metabolic and cardio
            exercise_categories = {
                'Push Day': ['push-up', 'dumbbell shoulder press', 'dip', 'tricep extension'],
                'Pull Day': ['pull-up', 'barbell row', 'lat pulldown', 'bicep curl'],
                'Leg Day': ['squat', 'lunge', 'leg press', 'calf raise'],
                'Cardio Focus': ['burpee', 'jump squat', 'mountain climber', 'high knees']
            }
        else:
            # Balanced strength and muscle building
            exercise_categories = {
                'Push Day': ['barbell bench press', 'dumbbell shoulder press', 'push-up', 'dip'],
                'Pull Day': ['pull-up', 'barbell row', 'lat pulldown', 'cable curl'],
                'Leg Day': ['barbell squat', 'deadlift', 'lunge', 'leg press']
            }
            
        self._render_exercise_categories(story, exercise_categories)
    
    def _add_endomorph_exercises(self, story: List, goal: str):
        """Add endomorph-specific exercises focusing on fat burning"""
        
        # High-intensity and metabolic focus
        exercise_categories = {
            'HIIT Circuit': ['burpee', 'jump squat', 'mountain climber', 'high knees'],
            'Strength + Cardio': ['thruster', 'kettlebell swing', 'battle rope', 'box jump'],
            'Bodyweight Power': ['push-up', 'pull-up', 'squat', 'lunge'],
            'Core + Stability': ['plank', 'russian twist', 'bicycle crunch', 'leg raise']
        }
        
        self._render_exercise_categories(story, exercise_categories)
    
    def _render_exercise_categories(self, story: List, exercise_categories: Dict):
        """Render exercise categories with detailed information from exercise loader"""
        
        for category_name, exercise_names in exercise_categories.items():
            story.append(Paragraph(f"{category_name}:", self.styles['SubsectionHeader']))
            
            # Create exercise table
            exercise_table_data = [['Exercise', 'Target Muscles', 'Equipment', 'Difficulty']]
            
            for exercise_name in exercise_names[:5]:  # Limit to 5 exercises per category
                # Search for exercise in our database
                exercise_matches = self.exercise_loader.search_exercises(exercise_name, limit=1)
                
                if exercise_matches:
                    exercise = exercise_matches[0]
                    target_muscles = ', '.join(exercise.get('targetMuscles', ['N/A'])[:2])  # Limit to 2
                    equipment = ', '.join(exercise.get('equipments', ['body weight'])[:2])  # Limit to 2
                    
                    # Determine difficulty based on equipment
                    if 'body weight' in equipment.lower():
                        difficulty = 'Beginner'
                    elif 'barbell' in equipment.lower() or 'dumbbell' in equipment.lower():
                        difficulty = 'Intermediate'
                    else:
                        difficulty = 'Intermediate'
                        
                    # Truncate long text
                    name = exercise.get('name', exercise_name)
                    if len(name) > 25:
                        name = name[:22] + "..."
                    if len(target_muscles) > 20:
                        target_muscles = target_muscles[:17] + "..."
                    if len(equipment) > 15:
                        equipment = equipment[:12] + "..."
                        
                    exercise_table_data.append([name, target_muscles, equipment, difficulty])
                else:
                    # Fallback for exercises not found in database
                    exercise_table_data.append([exercise_name, 'Full body', 'Various', 'Intermediate'])
            
            # Create and style the exercise table
            if len(exercise_table_data) > 1:  # Has data beyond header
                exercise_table = Table(exercise_table_data, colWidths=[5*cm, 4*cm, 3*cm, 3*cm])
                exercise_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_GRAY_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Exercise names left-aligned
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Target muscles left-aligned
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Equipment left-aligned
                    ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Difficulty centered
                    
                    # Grid and padding
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_SECONDARY])
                ]))
                story.append(exercise_table)
            
            story.append(Spacer(1, 10))
    
    def _add_fallback_exercise_recommendations(self, story: List, record_data: Dict):
        """Add basic fallback exercise recommendations when data is unavailable"""
        story.append(Paragraph("General Exercise Guidelines", self.styles['SubsectionHeader']))
        
        general_exercises = [
            "Aim for 150 minutes of moderate aerobic activity per week",
            "Include strength training exercises 2-3 days per week",
            "Focus on major muscle groups with compound movements",
            "Start with bodyweight exercises and progress gradually", 
            "Include flexibility and mobility work in your routine",
            "Allow adequate rest and recovery between training sessions"
        ]
        
        for exercise in general_exercises:
            story.append(Paragraph(f"• {exercise}", self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("For a personalized exercise program, please consult with a fitness professional.", self.styles['CustomBodyText']))
    
    def _add_training_strategy_summary(self, story: List, fitness_data: Dict):
        """Add training strategy summary"""
        story.append(Paragraph("Training Strategy", self.styles['SubsectionHeader']))
        
        # Extract strategy information
        strength_days = fitness_data.get('strength_days', 3)
        cardio_days = fitness_data.get('cardio_days', 2)
        rest_days = 7 - strength_days - cardio_days if strength_days + cardio_days <= 7 else 1
        focus = fitness_data.get('focus', 'Balanced training approach')
        fitness_strategy = fitness_data.get('fitness_strategy', 'Balanced approach')
        
        strategy_text = f"""
        <b>Weekly Training Split:</b><br/>
        • Strength Training: {strength_days} days per week<br/>
        • Cardiovascular Exercise: {cardio_days} days per week<br/>
        • Rest Days: {rest_days} days per week<br/>
        • Focus: {focus}<br/>
        • Strategy: {fitness_strategy}
        """
        story.append(Paragraph(strategy_text, self.styles['CustomBodyText']))
    
    def _add_exercise_categories(self, story: List, fitness_data: Dict, session_id: int):
        """Add exercise categories (gym vs bodyweight)"""
        story.append(Paragraph("Recommended Exercises", self.styles['SubsectionHeader']))
        
        # Get exercise data
        exercises = fitness_data.get('exercises', {})
        
        # Determine if gym or bodyweight based on available exercises
        has_gym_exercises = any(key in exercises for key in ['push', 'pull', 'legs', 'gym_exercises'])
        has_bodyweight_exercises = any(key in exercises for key in ['bodyweight', 'bodyweight_exercises'])
        
        if has_gym_exercises:
            self._add_gym_exercise_section(story, exercises)
        elif has_bodyweight_exercises:
            self._add_bodyweight_exercise_section(story, exercises)
        else:
            # Fallback: try to get exercise data from database
            self._add_fallback_exercise_section(story, session_id)
    
    def _add_gym_exercise_section(self, story: List, exercises: Dict):
        """Add gym exercise recommendations with push/pull/legs split"""
        story.append(Paragraph("Gym Training Program", self.styles['SubsectionHeader']))
        
        # Define the training split
        training_split = {
            'Push Day': exercises.get('push', exercises.get('push_exercises', [])),
            'Pull Day': exercises.get('pull', exercises.get('pull_exercises', [])),
            'Leg Day': exercises.get('legs', exercises.get('leg_exercises', []))
        }
        
        # If no specific split, try general gym exercises
        if not any(training_split.values()):
            gym_exercises = exercises.get('gym_exercises', [])
            if gym_exercises:
                training_split = {'Gym Exercises': gym_exercises}
        
        for category, exercise_list in training_split.items():
            if not exercise_list:
                continue
                
            story.append(Paragraph(f"<b>{category}:</b>", self.styles['SubsectionHeader']))
            
            # Create exercise table
            exercise_table_data = [['Exercise', 'Sets', 'Reps', 'Notes']]
            
            for exercise in exercise_list[:6]:  # Limit to 6 exercises per category
                if isinstance(exercise, dict):
                    name = exercise.get('name', exercise.get('exercise_name', 'Unknown Exercise'))
                    sets = exercise.get('sets', '3-4')
                    reps = exercise.get('reps', '8-12')
                    notes = exercise.get('notes', exercise.get('instructions', 'Focus on form'))
                    
                    # Truncate long notes
                    if len(str(notes)) > 30:
                        notes = str(notes)[:27] + "..."
                        
                elif isinstance(exercise, str):
                    name = exercise
                    sets = '3-4'
                    reps = '8-12'
                    notes = 'Focus on form'
                else:
                    name = 'Unknown Exercise'
                    sets = '3-4'  
                    reps = '8-12'
                    notes = 'Focus on form'
                
                exercise_table_data.append([name, str(sets), str(reps), str(notes)])
            
            # Create and style the exercise table
            if len(exercise_table_data) > 1:  # Has data beyond header
                exercise_table = Table(exercise_table_data, colWidths=[5*cm, 2*cm, 2*cm, 7*cm])
                exercise_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_GRAY_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Exercise names left-aligned
                    ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Sets and reps centered
                    ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Notes left-aligned
                    
                    # Grid and padding
                    ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_SECONDARY])
                ]))
                story.append(exercise_table)
            else:
                story.append(Paragraph(f"No specific exercises available for {category}.", self.styles['CustomBodyText']))
            
            story.append(Spacer(1, 12))
    
    def _add_bodyweight_exercise_section(self, story: List, exercises: Dict):
        """Add bodyweight exercise recommendations"""
        story.append(Paragraph("Bodyweight Training Program", self.styles['SubsectionHeader']))
        
        bodyweight_exercises = exercises.get('bodyweight', exercises.get('bodyweight_exercises', []))
        
        if not bodyweight_exercises:
            # Default bodyweight exercises
            bodyweight_exercises = [
                {'name': 'Push-ups', 'reps': '10-15', 'notes': 'Start with knee push-ups if needed'},
                {'name': 'Squats', 'reps': '15-20', 'notes': 'Keep chest up and knees behind toes'},
                {'name': 'Plank', 'reps': '30-60s', 'notes': 'Keep body in straight line'},
                {'name': 'Lunges', 'reps': '10-12 each leg', 'notes': 'Step back into lunge position'},
                {'name': 'Mountain Climbers', 'reps': '20-30', 'notes': 'Quick alternating leg movements'},
                {'name': 'Burpees', 'reps': '5-10', 'notes': 'Full body exercise, modify as needed'}
            ]
        
        # Create bodyweight exercise table
        bw_table_data = [['Exercise', 'Reps/Duration', 'Instructions']]
        
        for exercise in bodyweight_exercises[:8]:  # Limit to 8 exercises
            if isinstance(exercise, dict):
                name = exercise.get('name', exercise.get('exercise_name', 'Unknown Exercise'))
                reps = exercise.get('reps', exercise.get('duration', '10-15'))
                notes = exercise.get('notes', exercise.get('instructions', 'Focus on proper form'))
                
                # Truncate long instructions
                if len(str(notes)) > 40:
                    notes = str(notes)[:37] + "..."
                    
            elif isinstance(exercise, str):
                name = exercise
                reps = '10-15'
                notes = 'Focus on proper form'
            else:
                name = 'Unknown Exercise'
                reps = '10-15'
                notes = 'Focus on proper form'
            
            bw_table_data.append([name, str(reps), str(notes)])
        
        # Create and style the bodyweight exercise table
        bw_table = Table(bw_table_data, colWidths=[4*cm, 3*cm, 9*cm])
        bw_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_SUCCESS),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_GRAY_DARK),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Exercise names left-aligned
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Reps centered
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Instructions left-aligned
            
            # Grid and padding
            ('GRID', (0, 0), (-1, -1), 0.5, self.BRAND_GRAY_LIGHT),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_SECONDARY])
        ]))
        story.append(bw_table)
        
        # Add bodyweight training tips
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Bodyweight Training Tips:</b>", self.styles['SubsectionHeader']))
        tips = [
            "Start with 2-3 sets of each exercise",
            "Rest 30-60 seconds between sets",
            "Focus on proper form over speed",
            "Progress by increasing reps or duration",
            "Listen to your body and rest when needed"
        ]
        for tip in tips:
            story.append(Paragraph(f"• {tip}", self.styles['CustomBodyText']))
    
    def _add_fallback_exercise_section(self, story: List, session_id: int):
        """Add fallback exercise section when no specific data is found"""
        story.append(Paragraph("General Exercise Recommendations", self.styles['SubsectionHeader']))
        
        # General recommendations based on typical needs
        general_exercises = {
            'Strength Training': [
                'Push-ups or Chest Press',
                'Squats or Leg Press', 
                'Pull-ups or Lat Pulldown',
                'Deadlifts or Romanian Deadlifts',
                'Overhead Press',
                'Planks'
            ],
            'Cardiovascular': [
                'Brisk Walking (30-45 minutes)',
                'Cycling or Stationary Bike',
                'Swimming',
                'High-Intensity Interval Training (HIIT)',
                'Rowing Machine',
                'Dancing or Aerobics'
            ]
        }
        
        for category, exercises in general_exercises.items():
            story.append(Paragraph(f"<b>{category}:</b>", self.styles['SubsectionHeader']))
            for exercise in exercises:
                story.append(Paragraph(f"• {exercise}", self.styles['CustomBodyText']))
            story.append(Spacer(1, 8))
    
    def _add_footer(self, story: List, record_data: Dict):
        """Add report footer"""
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=self.BRAND_GRAY_LIGHT))
        story.append(Spacer(1, 10))
        
        footer_text = f"""
        <i>This personalized diet and exercise plan was generated by the Somatotype-Based Diet Recommendation System
        on {datetime.now().strftime('%B %d, %Y')}. Please consult with healthcare professionals before making 
        significant changes to your diet or exercise routine.</i>
        """
        story.append(Paragraph(footer_text, self.styles['CustomCaption']))
    
    def _prepare_image_for_pdf(self, image_path: str, max_width: float, max_height: float) -> Optional[Image]:
        """Prepare image for PDF inclusion with proper sizing"""
        try:
            # Open image and get dimensions
            pil_img = PILImage.open(image_path)
            img_width, img_height = pil_img.size
            
            # Calculate scaling factor to fit within max dimensions
            width_scale = max_width / (img_width / 72)  # Convert pixels to points
            height_scale = max_height / (img_height / 72)
            scale = min(width_scale, height_scale, 1.0)  # Don't upscale
            
            # Calculate final dimensions
            final_width = (img_width / 72) * scale
            final_height = (img_height / 72) * scale
            
            return Image(image_path, width=final_width, height=final_height)
            
        except Exception as e:
            print(f"Error preparing image {image_path}: {e}")
            return None
    
    def _has_images(self, record_data: Dict) -> bool:
        """Check if record has captured images"""
        front_image = record_data.get('front_image_path')
        side_image = record_data.get('side_image_path')
        
        return ((front_image and os.path.exists(front_image)) or 
                (side_image and os.path.exists(side_image)))
    
    def _format_date(self, date_string: str) -> str:
        """Format date string for display"""
        if not date_string:
            return "Unknown Date"
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_string


def create_export_directory() -> str:
    """Create export directory if it doesn't exist"""
    export_dir = os.path.join(PROJECT_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def generate_export_filename(record_data: Dict, is_history: bool = False) -> str:
    """Generate a descriptive filename for the export"""
    name = record_data.get('name', 'User').replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if is_history:
        session_date = record_data.get('session_date', '')
        if session_date:
            try:
                dt = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
                date_str = dt.strftime("%Y%m%d")
                return f"Diet_Analysis_{name}_{date_str}_{timestamp}.pdf"
            except:
                pass
        return f"Diet_Analysis_History_{name}_{timestamp}.pdf"
    else:
        return f"Diet_Plan_{name}_{timestamp}.pdf"


# Example usage and testing
if __name__ == "__main__":
    # Test data
    test_record = {
        'session_id': 1,
        'name': 'John Doe',
        'gender': 'male',
        'age': 25,
        'goal': 'Build Muscle',
        'session_date': '2024-01-15T10:30:00',
        'calories': 2500,
        'front_image_path': '',
        'side_image_path': '',
        'somatotype_class': 'Mesomorph'
    }
    
    # Create exporter
    exporter = PDFExporter()
    
    # Test export
    export_dir = create_export_directory()
    filename = generate_export_filename(test_record)
    output_path = os.path.join(export_dir, filename)
    
    success = exporter.export_current_diet_plan(test_record, output_path)
    print(f"Export {'successful' if success else 'failed'}: {output_path}")