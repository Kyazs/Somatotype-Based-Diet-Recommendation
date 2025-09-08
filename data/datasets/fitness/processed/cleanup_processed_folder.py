#!/usr/bin/env python3
"""
Processed Folder Cleanup Script

This script cleans the processed folder, removing all generated datasets
while keeping only the essential processing scripts.

Use this to maintain a clean repository or reset the environment.

"""

import os
import glob
import shutil

def clean_processed_folder():
    """Clean the processed folder of all generated datasets"""
    
    # Get current directory (should be the processed folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🧹 Cleaning Processed Folder")
    print("=" * 40)
    print(f"📂 Location: {current_dir}")
    print()
    
    # Files to keep (essential scripts and documentation)
    keep_files = {
        'process_universal_fitness.py',
        'universal_recommendation_engine.py', 
        'demo_universal_system.py',
        'process_evidence_based_fitness.py',
        'README_SCRIPTS.md',
        'cleanup_processed_folder.py'  # This script itself
    }
    
    # Get all files in the directory
    all_files = set(os.listdir(current_dir))
    
    # Files to remove
    files_to_remove = all_files - keep_files
    
    # Remove directories like __pycache__
    for item in files_to_remove.copy():
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path):
            print(f"🗂️  Removing directory: {item}")
            shutil.rmtree(item_path)
            files_to_remove.remove(item)
    
    # Remove files
    removed_count = 0
    for file in files_to_remove:
        file_path = os.path.join(current_dir, file)
        try:
            os.remove(file_path)
            print(f"🗑️  Removed: {file}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {file}: {e}")
    
    print()
    print(f"✅ Cleanup Complete!")
    print(f"   • Removed {removed_count} files")
    print(f"   • Kept {len(keep_files)} essential scripts")
    print()
    
    print("📁 Remaining Files:")
    remaining_files = [f for f in os.listdir(current_dir) if not f.startswith('.')]
    for file in sorted(remaining_files):
        print(f"   • {file}")
    
    print()
    print("🚀 Ready for Fresh Dataset Generation!")
    print("   Run: python process_universal_fitness.py")

if __name__ == "__main__":
    clean_processed_folder()
