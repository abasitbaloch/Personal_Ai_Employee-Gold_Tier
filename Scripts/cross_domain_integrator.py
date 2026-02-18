#!/usr/bin/env python3
"""
Cross-Domain Integrator - Gold Tier Skill
Automatically categorizes tasks in /Needs_Action into Personal and Business domains.
"""

import os
import re
from pathlib import Path

# Business keywords for classification
BUSINESS_KEYWORDS = [
    'client', 'invoice', 'revenue', 'project', 'meeting', 'proposal',
    'contract', 'deadline', 'budget', 'sales', 'marketing', 'business',
    'professional', 'work', 'company', 'customer', 'payment', 'subscription',
    'linkedin', 'networking', 'presentation', 'report', 'quarterly'
]

# Personal keywords for classification
PERSONAL_KEYWORDS = [
    'personal', 'family', 'health', 'fitness', 'vacation', 'hobby',
    'home', 'shopping', 'birthday', 'appointment', 'doctor', 'dentist',
    'grocery', 'entertainment', 'friend', 'weekend', 'holiday'
]


def classify_task(file_path):
    """
    Classify a task file as 'Business' or 'Personal' based on content analysis.

    Args:
        file_path: Path to the .md task file

    Returns:
        str: 'Business' or 'Personal'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        business_score = sum(1 for keyword in BUSINESS_KEYWORDS if keyword in content)
        personal_score = sum(1 for keyword in PERSONAL_KEYWORDS if keyword in content)

        # Default to Business if no clear classification
        return 'Business' if business_score >= personal_score else 'Personal'

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 'Business'  # Default to Business on error


def process_needs_action():
    """
    Scan /Needs_Action folder and categorize all .md files into subfolders.
    """
    # Get the vault root directory (parent of Scripts folder)
    vault_root = Path(__file__).parent.parent
    needs_action_dir = vault_root / 'Needs_Action'

    if not needs_action_dir.exists():
        print(f"Error: {needs_action_dir} does not exist")
        return

    # Create subdirectories if they don't exist
    personal_dir = needs_action_dir / 'Personal'
    business_dir = needs_action_dir / 'Business'

    personal_dir.mkdir(exist_ok=True)
    business_dir.mkdir(exist_ok=True)

    # Process all .md files in the root of Needs_Action
    processed_count = {'Business': 0, 'Personal': 0}

    for file_path in needs_action_dir.glob('*.md'):
        if file_path.is_file():
            category = classify_task(file_path)

            # Determine destination
            dest_dir = business_dir if category == 'Business' else personal_dir
            dest_path = dest_dir / file_path.name

            # Move the file
            try:
                file_path.rename(dest_path)
                processed_count[category] += 1
                print(f"Moved {file_path.name} -> {category}/")
            except Exception as e:
                print(f"Error moving {file_path.name}: {e}")

    print(f"\n[SUCCESS] Cross-Domain Integration Complete")
    print(f"  Business tasks: {processed_count['Business']}")
    print(f"  Personal tasks: {processed_count['Personal']}")


if __name__ == '__main__':
    process_needs_action()
