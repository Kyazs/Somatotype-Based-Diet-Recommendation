import json
import csv
import html

def generate_embedded_html():
    """Generate HTML file with all data embedded to avoid CORS issues"""
    
    print("Loading exercise data...")
    
    # Load exercise data
    with open('exercises.json', 'r') as f:
        gym_exercises = json.load(f)
    
    with open('outdoor_exercises.json', 'r') as f:
        bodyweight_exercises = json.load(f)
    
    print(f"Loaded {len(gym_exercises)} gym exercises and {len(bodyweight_exercises)} bodyweight exercises")
    
    # Load CSV data
    templates = []
    with open('enhanced_diet_templates_with_exercise_ids.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            templates.append(row)
    
    print(f"Loaded {len(templates)} templates")
    
    # Remove duplicates based on unique combination
    seen = set()
    unique_templates = []
    for template in templates:
        key = f"{template['somatotype']}-{template['gender']}-{template['goal']}-{template['exercise_type']}-{template['exercise_complexity']}"
        if key not in seen:
            seen.add(key)
            unique_templates.append(template)
    
    print(f"Found {len(unique_templates)} unique templates")
    
    # Create the HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exercise Recommendation Visualizer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        .controls {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .filter-section {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .filter-group label {{
            font-weight: 600;
            color: #555;
            font-size: 0.9rem;
        }}

        select, input {{
            padding: 8px 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: border-color 0.3s;
        }}

        select:focus, input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .template-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 25px;
        }}

        .template-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .template-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}

        .template-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }}

        .template-title {{
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .template-subtitle {{
            opacity: 0.9;
            font-size: 1rem;
        }}

        .template-body {{
            padding: 25px;
        }}

        .template-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .detail-label {{
            font-weight: 600;
            color: #666;
        }}

        .detail-value {{
            color: #333;
            font-weight: 500;
        }}

        .exercises-section {{
            margin-top: 25px;
        }}

        .exercise-category {{
            margin-bottom: 25px;
        }}

        .category-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .category-icon {{
            width: 24px;
            height: 24px;
            background: #667eea;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.8rem;
        }}

        .exercise-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .exercise-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 2px solid transparent;
        }}

        .exercise-item:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}

        .exercise-gif {{
            width: 100%;
            height: 150px;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .exercise-gif img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }}

        .exercise-gif.no-gif {{
            color: #6c757d;
            font-size: 0.8rem;
        }}

        .exercise-name {{
            font-weight: 600;
            color: #333;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}

        .exercise-details {{
            font-size: 0.8rem;
            color: #666;
        }}

        .stats {{
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .template-grid {{
                grid-template-columns: 1fr;
            }}
            
            .template-details {{
                grid-template-columns: 1fr;
            }}
            
            .filter-section {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .exercise-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏋️ Exercise Recommendation Visualizer</h1>
            <p>Comprehensive Somatotype-Based Diet and Fitness Templates with Exercise GIF Demonstrations</p>
        </div>

        <div class="controls">
            <div class="filter-section">
                <div class="filter-group">
                    <label for="somatotypeFilter">Somatotype:</label>
                    <select id="somatotypeFilter">
                        <option value="">All Somatotypes</option>
                        <option value="endomorph">Endomorph</option>
                        <option value="ectomorph">Ectomorph</option>
                        <option value="mesomorph">Mesomorph</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="genderFilter">Gender:</label>
                    <select id="genderFilter">
                        <option value="">All Genders</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="goalFilter">Goal:</label>
                    <select id="goalFilter">
                        <option value="">All Goals</option>
                        <option value="weight_loss">Weight Loss</option>
                        <option value="muscle_gain">Muscle Gain</option>
                        <option value="maintenance">Maintenance</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="exerciseTypeFilter">Exercise Type:</label>
                    <select id="exerciseTypeFilter">
                        <option value="">All Types</option>
                        <option value="gym">Gym</option>
                        <option value="bodyweight">Bodyweight</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="complexityFilter">Complexity:</label>
                    <select id="complexityFilter">
                        <option value="">All Levels</option>
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="limitFilter">Display Limit:</label>
                    <select id="limitFilter">
                        <option value="10">10 Templates</option>
                        <option value="20">20 Templates</option>
                        <option value="50">50 Templates</option>
                        <option value="all">All Templates</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="stats" id="statsContainer"></div>
        <div class="template-grid" id="templateContainer"></div>
    </div>

    <script>
        // Embedded data to avoid CORS issues
        const allTemplates = {json.dumps(unique_templates)};
        const gymExercises = {json.dumps({ex["exerciseId"]: ex for ex in gym_exercises})};
        const bodyweightExercises = {json.dumps({ex["exerciseId"]: ex for ex in bodyweight_exercises})};

        function getExerciseDetails(exerciseId, isBodyweight = false) {{
            const exercise = isBodyweight ? bodyweightExercises[exerciseId] : gymExercises[exerciseId];
            return exercise || {{ name: `Exercise ${{exerciseId}}`, gifUrl: '', targetMuscles: [], equipments: [] }};
        }}

        function renderExerciseCategory(title, exerciseIds, isBodyweight = false, icon = 'E') {{
            if (!exerciseIds || exerciseIds.trim() === '') return '';

            const ids = exerciseIds.split(',').map(id => id.trim()).filter(id => id);
            if (ids.length === 0) return '';

            const exerciseItems = ids.map(id => {{
                const exercise = getExerciseDetails(id, isBodyweight);
                const gifHTML = exercise.gifUrl ? 
                    `<img src="${{exercise.gifUrl}}" alt="${{exercise.name}}" onerror="this.parentElement.classList.add('no-gif'); this.parentElement.innerHTML='GIF not available'">` : 
                    '';
                
                return `
                    <div class="exercise-item">
                        <div class="exercise-gif ${{!exercise.gifUrl ? 'no-gif' : ''}}">
                            ${{exercise.gifUrl ? gifHTML : 'GIF not available'}}
                        </div>
                        <div class="exercise-name">${{exercise.name}}</div>
                        <div class="exercise-details">
                            <div>Target: ${{Array.isArray(exercise.targetMuscles) ? exercise.targetMuscles.join(', ') : 'N/A'}}</div>
                            <div>Equipment: ${{Array.isArray(exercise.equipments) ? exercise.equipments.join(', ') : 'N/A'}}</div>
                        </div>
                    </div>
                `;
            }}).join('');

            return `
                <div class="exercise-category">
                    <div class="category-title">
                        <div class="category-icon">${{icon}}</div>
                        ${{title}} (${{ids.length}} exercises)
                    </div>
                    <div class="exercise-grid">
                        ${{exerciseItems}}
                    </div>
                </div>
            `;
        }}

        function renderTemplate(template) {{
            const isGymType = template.exercise_type === 'gym';
            
            let exercisesHTML = '';
            
            if (isGymType) {{
                exercisesHTML = `
                    ${{renderExerciseCategory('Push Exercises', template.push_exercises, false, 'P')}}
                    ${{renderExerciseCategory('Pull Exercises', template.pull_exercises, false, 'Pu')}}
                    ${{renderExerciseCategory('Legs Exercises', template.legs_exercises, false, 'L')}}
                `;
            }} else {{
                exercisesHTML = renderExerciseCategory('Bodyweight Exercises', template.bodyweight_exercises, true, 'B');
            }}

            if (!exercisesHTML.trim()) {{
                exercisesHTML = '<div class="no-results">No exercises found for this template.</div>';
            }}

            return `
                <div class="template-card">
                    <div class="template-header">
                        <div class="template-title">
                            ${{template.somatotype.charAt(0).toUpperCase() + template.somatotype.slice(1)}} - 
                            ${{template.gender.charAt(0).toUpperCase() + template.gender.slice(1)}}
                        </div>
                        <div class="template-subtitle">
                            ${{template.goal.replace('_', ' ').charAt(0).toUpperCase() + template.goal.replace('_', ' ').slice(1)}} • 
                            ${{template.exercise_complexity.charAt(0).toUpperCase() + template.exercise_complexity.slice(1)}} • 
                            ${{template.exercise_type.charAt(0).toUpperCase() + template.exercise_type.slice(1)}}
                        </div>
                    </div>
                    <div class="template-body">
                        <div class="template-details">
                            <div class="detail-item">
                                <span class="detail-label">Activity Level:</span>
                                <span class="detail-value">${{template.activity_level.replace('_', ' ')}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Total Calories:</span>
                                <span class="detail-value">${{template.total_calories}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Protein:</span>
                                <span class="detail-value">${{template.protein_g}}g (${{template.protein_pct}}%)</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Carbs:</span>
                                <span class="detail-value">${{template.carbs_g}}g (${{template.carbs_pct}}%)</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Fats:</span>
                                <span class="detail-value">${{template.fats_g}}g (${{template.fats_pct}}%)</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Training Split:</span>
                                <span class="detail-value">${{template.fitness_split_strength}}x Strength, ${{template.fitness_split_cardio}}x Cardio</span>
                            </div>
                        </div>
                        
                        <div class="exercises-section">
                            ${{exercisesHTML}}
                        </div>
                    </div>
                </div>
            `;
        }}

        function renderTemplates(templates) {{
            const container = document.getElementById('templateContainer');
            const limit = document.getElementById('limitFilter').value;
            const displayTemplates = limit === 'all' ? templates : templates.slice(0, parseInt(limit));
            
            if (displayTemplates.length === 0) {{
                container.innerHTML = '<div class="no-results">No templates match the current filters.</div>';
                return;
            }}

            container.innerHTML = displayTemplates.map(renderTemplate).join('');
        }}

        function filterTemplates() {{
            const somatotype = document.getElementById('somatotypeFilter').value;
            const gender = document.getElementById('genderFilter').value;
            const goal = document.getElementById('goalFilter').value;
            const exerciseType = document.getElementById('exerciseTypeFilter').value;
            const complexity = document.getElementById('complexityFilter').value;

            const filtered = allTemplates.filter(template => {{
                return (!somatotype || template.somatotype === somatotype) &&
                       (!gender || template.gender === gender) &&
                       (!goal || template.goal === goal) &&
                       (!exerciseType || template.exercise_type === exerciseType) &&
                       (!complexity || template.exercise_complexity === complexity);
            }});

            renderTemplates(filtered);
            updateStats(filtered);
        }}

        function updateStats(templates) {{
            const stats = document.getElementById('statsContainer');
            const totalExercises = templates.reduce((count, template) => {{
                const isGym = template.exercise_type === 'gym';
                if (isGym) {{
                    const pushCount = template.push_exercises ? template.push_exercises.split(',').filter(id => id.trim()).length : 0;
                    const pullCount = template.pull_exercises ? template.pull_exercises.split(',').filter(id => id.trim()).length : 0;
                    const legsCount = template.legs_exercises ? template.legs_exercises.split(',').filter(id => id.trim()).length : 0;
                    return count + pushCount + pullCount + legsCount;
                }} else {{
                    const bodyweightCount = template.bodyweight_exercises ? template.bodyweight_exercises.split(',').filter(id => id.trim()).length : 0;
                    return count + bodyweightCount;
                }}
            }}, 0);

            stats.innerHTML = `
                <strong>Showing ${{templates.length}} unique templates</strong> • 
                Total exercises displayed: ${{totalExercises}} • 
                Gym exercises in database: ${{Object.keys(gymExercises).length}} • 
                Bodyweight exercises in database: ${{Object.keys(bodyweightExercises).length}}
            `;
        }}

        // Event listeners
        document.getElementById('somatotypeFilter').addEventListener('change', filterTemplates);
        document.getElementById('genderFilter').addEventListener('change', filterTemplates);
        document.getElementById('goalFilter').addEventListener('change', filterTemplates);
        document.getElementById('exerciseTypeFilter').addEventListener('change', filterTemplates);
        document.getElementById('complexityFilter').addEventListener('change', filterTemplates);
        document.getElementById('limitFilter').addEventListener('change', filterTemplates);

        // Initialize
        renderTemplates(allTemplates);
        updateStats(allTemplates);
    </script>
</body>
</html>'''
    
    # Write the HTML file
    with open('exercise_visualizer_embedded.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Created 'exercise_visualizer_embedded.html' with all data embedded!")
    print(f"📊 Total unique templates: {len(unique_templates)}")
    print(f"🏋️ Gym exercises: {len(gym_exercises)}")
    print(f"🤸 Bodyweight exercises: {len(bodyweight_exercises)}")

if __name__ == "__main__":
    generate_embedded_html()