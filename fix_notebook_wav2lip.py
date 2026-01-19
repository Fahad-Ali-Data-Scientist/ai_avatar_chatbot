"""
Automatic fix for Wav2Lip temp directory error in notebook
Run this script to update your notebook automatically
"""

import json
from pathlib import Path

def fix_notebook():
    """Fix the notebook to create temp directory for Wav2Lip"""
    
    notebook_path = Path("talking_avatar_complete.ipynb")
    
    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        return False
    
    print(f"📖 Reading notebook: {notebook_path}")
    
    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Find and fix the LipSyncGenerator cell (should be cell 10)
    fixed = False
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Check if this is the LipSyncGenerator class
            if 'class LipSyncGenerator:' in source and 'def __init__' in source:
                print(f"✓ Found LipSyncGenerator class in cell {i}")
                
                # Check if already fixed
                if 'temp_dir' in source and 'mkdir' in source:
                    print(f"  Already fixed! Skipping...")
                    continue
                
                # Fix the __init__ method
                lines = cell['source']
                new_lines = []
                
                for j, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # After the checkpoint check, add temp dir creation
                    if 'print(f"✓ Lip-sync generator initialized")' in line:
                        # Insert before this line
                        new_lines.pop()  # Remove the print line we just added
                        
                        # Add temp directory creation
                        new_lines.append('        \n')
                        new_lines.append('        # Create temp directory for Wav2Lip (required for audio processing)\n')
                        new_lines.append('        temp_dir = self.wav2lip_path / "temp"\n')
                        new_lines.append('        temp_dir.mkdir(exist_ok=True)\n')
                        new_lines.append('        \n')
                        new_lines.append(line)  # Re-add the print line
                        new_lines.append('        print(f"  Temp directory created: {temp_dir}")\n')
                
                cell['source'] = new_lines
                print(f"  ✓ Fixed __init__ method")
                fixed = True
            
            # Also fix the generate_talking_video method
            if 'def generate_talking_video(' in source and not fixed:
                print(f"  Checking generate_talking_video method in cell {i}")
                
                # Check if already fixed
                if 'temp_dir = self.wav2lip_path / "temp"' in source and 'mkdir' in source:
                    print(f"  Already fixed! Skipping...")
                    continue
                
                lines = cell['source']
                new_lines = []
                
                for j, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # After the docstring, add temp dir creation
                    if 'inference_script = self.wav2lip_path / "inference.py"' in line:
                        # Insert before this line
                        new_lines.pop()  # Remove the line we just added
                        
                        new_lines.append('        # Ensure temp directory exists\n')
                        new_lines.append('        temp_dir = self.wav2lip_path / "temp"\n')
                        new_lines.append('        temp_dir.mkdir(exist_ok=True)\n')
                        new_lines.append('        \n')
                        new_lines.append(line)  # Re-add the line
                
                cell['source'] = new_lines
                print(f"  ✓ Fixed generate_talking_video method")
                fixed = True
    
    if fixed:
        # Save the fixed notebook
        backup_path = notebook_path.with_suffix('.ipynb.backup')
        print(f"\n💾 Creating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        print(f"💾 Saving fixed notebook: {notebook_path}")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        print("\n✅ Notebook fixed successfully!")
        print("\nChanges made:")
        print("  1. Added temp directory creation in LipSyncGenerator.__init__()")
        print("  2. Added temp directory check in generate_talking_video()")
        print("\n📝 A backup was created: talking_avatar_complete.ipynb.backup")
        print("\n🚀 You can now run the notebook without the temp directory error!")
        return True
    else:
        print("\n⚠️  LipSyncGenerator class not found or already fixed")
        return False


def create_temp_directories():
    """Manually create the temp directories as a fallback"""
    print("\n📁 Creating temp directories manually...")
    
    wav2lip_path = Path("Wav2Lip")
    if not wav2lip_path.exists():
        print(f"❌ Wav2Lip directory not found: {wav2lip_path}")
        print("   Please make sure Wav2Lip is cloned in the current directory")
        return False
    
    temp_dir = wav2lip_path / "temp"
    temp_dir.mkdir(exist_ok=True)
    print(f"✓ Created: {temp_dir}")
    
    # Also create results directory (sometimes needed)
    results_dir = wav2lip_path / "results"
    results_dir.mkdir(exist_ok=True)
    print(f"✓ Created: {results_dir}")
    
    return True


if __name__ == "__main__":
    print("="*70)
    print("  WAV2LIP TEMP DIRECTORY FIX")
    print("="*70)
    print()
    print("This script will:")
    print("  1. Update your notebook to automatically create temp directories")
    print("  2. Create the temp directories manually as a backup")
    print()
    
    # Try to fix the notebook
    notebook_fixed = fix_notebook()
    
    # Also create directories manually
    print()
    dirs_created = create_temp_directories()
    
    print()
    print("="*70)
    if notebook_fixed or dirs_created:
        print("✅ SUCCESS!")
        print()
        if notebook_fixed:
            print("  ✓ Notebook updated")
        if dirs_created:
            print("  ✓ Temp directories created")
        print()
        print("You can now run your notebook without the temp directory error!")
    else:
        print("⚠️  MANUAL FIX REQUIRED")
        print()
        print("Please manually create the directory:")
        print("  mkdir -p Wav2Lip/temp")
        print()
        print("Or see FIX_WAV2LIP_TEMP_ERROR.md for detailed instructions")
    print("="*70)
