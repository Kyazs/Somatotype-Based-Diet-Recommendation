# Fitness Dataset Processing Scripts

## 📂 Clean Processing Environment

This folder contains **only the processing scripts** needed to generate the fitness datasets. All datasets have been removed to keep the repository clean and allow users to generate fresh data when needed.

## 🚀 Available Scripts

### 1. **`process_universal_fitness.py`**
**Purpose**: Creates the universal fitness database from raw JSON data
```bash
python process_universal_fitness.py
```
**What it does**:
- Processes 1,500 exercises from JSON files
- Creates 8 training category files
- Generates goal-specific and activity-level files
- Creates the master universal database

### 2. **`universal_recommendation_engine.py`**
**Purpose**: Generates personalized recommendations for any user input
```bash
python universal_recommendation_engine.py
```
**What it does**:
- Takes user input in CSV format: `Name,Age,Goal,Activity_Level`
- Generates personalized exercise recommendations (20 per user)
- Creates optimized diet plans (6 per user)
- Produces complete user profile analysis

### 3. **`demo_universal_system.py`**
**Purpose**: Demonstrates the system with your exact example format
```bash
python demo_universal_system.py
```
**What it does**:
- Shows how the system handles the Casper example
- Displays top exercise and diet recommendations
- Demonstrates all system capabilities

### 4. **`cleanup_processed_folder.py`**
**Purpose**: Cleans the folder of all generated datasets, keeping only scripts
```bash
python cleanup_processed_folder.py
```
**What it does**:
- Removes all CSV dataset files
- Removes all JSON result files
- Removes temporary files and cache
- Keeps only essential processing scripts
- Maintains a clean repository state

## 🎯 First Time Setup

### Step 1: Generate the Universal Database
```bash
python process_universal_fitness.py
```
This will create:
- Universal exercises database (1,500 exercises)
- 8 training category files  
- 5 goal-specific files (300 exercises each)
- 5 activity-level files (250 exercises each)
- System summary and metadata

### Step 2: Test the System
```bash
python demo_universal_system.py
```
This will:
- Create example user inputs
- Generate sample recommendations
- Show system capabilities

### Step 3: Process Your Own Users
```bash
python universal_recommendation_engine.py
```

## 📝 How to Use with Your Own Data

### Step 1: Create User Input File
Create a CSV file with this exact format:
```csv
Name,Age,Goal,Activity_Level
casper,21,Maintain Weight,Moderately active
alice,35,Lose Weight,Lightly active
bob,28,Build Muscle,Very active
```

### Step 2: Run the Recommendation Engine
```bash
python universal_recommendation_engine.py
```

### Step 3: Check Results
The system automatically generates:
- `user_exercises_[name].csv` - 20 personalized exercises
- `user_diet_[name].csv` - 6 optimized meal plans
- `user_profile_[name].json` - complete analysis

## 🎯 Supported User Parameters

### Goals:
- **Maintain Weight** - Balanced strength + cardio
- **Lose Weight** - High calorie burn + metabolic focus
- **Gain Weight** - Muscle building + strength focus
- **Build Muscle** - Hypertrophy + progressive overload
- **Improve Fitness** - General fitness + functional movement

### Activity Levels:
- **Sedentary** - 3x/week, 30min, simple exercises
- **Lightly Active** - 3x/week, 40min, basic complexity
- **Moderately Active** - 4x/week, 45min, moderate complexity
- **Very Active** - 5x/week, 60min, advanced exercises
- **Extremely Active** - 6x/week, 75min, complex movements

### Ages:
- **Young Adult (18-30)** - High intensity, complex movements
- **Adult (31-45)** - Balanced approach, standard progression
- **Middle-aged (46-60)** - Injury prevention, moderate intensity
- **Older Adult (61+)** - Functional focus, balance emphasis

## 📊 What Gets Generated

When you run the scripts, they will create these files in this folder:

### Database Files:
- `universal_exercises_database.csv` - Master database (1,500 exercises)
- `universal_[category].csv` - Training category files (8 categories)
- `goal_[goal]_top_exercises.csv` - Goal-optimized files (300 exercises each)
- `activity_[level]_suitable_exercises.csv` - Activity-matched files (250 exercises each)
- `universal_fitness_system_summary.json` - System statistics

### User Results:
- `user_exercises_[name].csv` - Individual exercise recommendations
- `user_diet_[name].csv` - Individual diet plans
- `user_profile_[name].json` - Complete user analysis
- `example_user_inputs.csv` - Sample input file

## 🧹 Maintenance

### Clean the Folder
```bash
python cleanup_processed_folder.py
```
This removes all generated datasets and keeps only the processing scripts, useful for:
- Maintaining a clean repository
- Resetting the environment
- Reducing file clutter
- Preparing for fresh data generation

### 5. **`process_evidence_based_fitness.py`**
**Purpose**: Original evidence-based processing script (legacy)
```bash
python process_evidence_based_fitness.py
```

## 🧹 Clean Environment Benefits

✅ **Small Repository** - No large dataset files in version control  
✅ **Fresh Data** - Generate up-to-date datasets when needed  
✅ **Customizable** - Modify scripts before generating data  
✅ **Fast Clone** - Quick repository downloads  
✅ **Clear Purpose** - Scripts-only folder is self-explanatory  

## 🔧 Script Dependencies

All scripts use relative paths and will work correctly when run from this `processed` folder. The scripts automatically:
- Find the diet database (`diet_templates.csv`) in the main project directory
- Save all outputs to the current `processed` folder
- Load existing databases from the current directory

## 🌟 Key Features

✅ **Self-contained** - All scripts and data in one folder  
✅ **Portable** - Scripts use relative paths  
✅ **Universal** - Handles any valid user input  
✅ **Evidence-based** - ACSM & NSCA guidelines  
✅ **Production-ready** - Complete error handling  

## 📞 Usage Examples

### Quick Test with Demo:
```bash
python demo_universal_system.py
```

### Process Multiple Users:
1. Create `my_users.csv`:
```csv
Name,Age,Goal,Activity_Level
john,25,Build Muscle,Very active
mary,45,Lose Weight,Moderately active
```

2. Modify `universal_recommendation_engine.py` main function to use your file
3. Run: `python universal_recommendation_engine.py`

### Regenerate Database:
```bash
python process_universal_fitness.py
```

---

**All scripts are now self-contained in this processed folder and ready for immediate use!**
