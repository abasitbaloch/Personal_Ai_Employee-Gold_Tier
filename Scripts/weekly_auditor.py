#!/usr/bin/env python3
"""
Weekly Auditor - Gold Tier CEO Briefing Generator
Generates executive-level business intelligence reports.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import re

# Paths
VAULT_ROOT = Path(__file__).parent.parent
BUSINESS_GOALS = VAULT_ROOT / 'Business_Goals.md'
DONE_DIR = VAULT_ROOT / 'Done'
LOGS_DIR = VAULT_ROOT / 'Logs'


def setup_directories():
    """Create necessary directories if they don't exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def read_business_goals():
    """
    Read and parse Business_Goals.md to extract targets.

    Returns:
        dict: Business goals and targets
    """
    goals = {
        'monthly_revenue_target': 10000,
        'current_mtd': 4500,
        'active_projects': [],
        'key_metrics': {}
    }

    if not BUSINESS_GOALS.exists():
        return goals

    with open(BUSINESS_GOALS, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract monthly revenue target
    revenue_match = re.search(r'Monthly goal:\s*\$?([\d,]+)', content)
    if revenue_match:
        goals['monthly_revenue_target'] = int(revenue_match.group(1).replace(',', ''))

    # Extract current MTD
    mtd_match = re.search(r'Current MTD:\s*\$?([\d,]+)', content)
    if mtd_match:
        goals['current_mtd'] = int(mtd_match.group(1).replace(',', ''))

    # Extract active projects
    project_matches = re.findall(r'Project\s+(\w+)\s+Due\s+(.+)', content)
    goals['active_projects'] = [{'name': name, 'due': due} for name, due in project_matches]

    return goals


def scan_completed_tasks():
    """
    Scan /Done/ folder to count completed tasks by category.

    Returns:
        dict: Task counts by category
    """
    task_counts = {
        'total': 0,
        'business': 0,
        'personal': 0,
        'social_media': 0,
        'emails': 0,
        'documents': 0
    }

    if not DONE_DIR.exists():
        return task_counts

    # Count all .md files in Done directory
    for file_path in DONE_DIR.rglob('*.md'):
        task_counts['total'] += 1

        # Categorize by filename pattern
        filename = file_path.name
        if 'SOCIAL_MSG' in filename:
            task_counts['social_media'] += 1
        elif 'EMAIL' in filename:
            task_counts['emails'] += 1
        elif 'Business' in str(file_path):
            task_counts['business'] += 1
        elif 'Personal' in str(file_path):
            task_counts['personal'] += 1
        else:
            task_counts['documents'] += 1

    return task_counts


def calculate_mock_revenue(task_counts):
    """
    Calculate mock revenue based on completed tasks.
    This is a simplified model for demonstration.

    Args:
        task_counts: Dictionary of completed task counts

    Returns:
        int: Estimated revenue
    """
    # Revenue estimation model
    revenue = 0
    revenue += task_counts['business'] * 500  # $500 per business task
    revenue += task_counts['social_media'] * 200  # $200 per social lead
    revenue += task_counts['emails'] * 100  # $100 per email handled

    return revenue


def identify_bottlenecks():
    """
    Identify potential bottlenecks in the workflow.

    Returns:
        list: List of identified bottlenecks
    """
    bottlenecks = []

    # Check Pending_Approval folder
    pending_dir = VAULT_ROOT / 'Pending_Approval'
    if pending_dir.exists():
        pending_count = len(list(pending_dir.glob('*.md')))
        if pending_count > 5:
            bottlenecks.append(f"High volume in Pending_Approval ({pending_count} items) - review backlog")

    # Check Needs_Action folder
    needs_action_dir = VAULT_ROOT / 'Needs_Action'
    if needs_action_dir.exists():
        action_count = len(list(needs_action_dir.rglob('*.md')))
        if action_count > 10:
            bottlenecks.append(f"Task queue building up ({action_count} items) - increase processing frequency")

    # Check for old files
    if DONE_DIR.exists():
        week_ago = datetime.now() - timedelta(days=7)
        recent_files = [f for f in DONE_DIR.rglob('*.md') if datetime.fromtimestamp(f.stat().st_mtime) > week_ago]
        if len(recent_files) < 5:
            bottlenecks.append("Low task completion rate this week - investigate workflow efficiency")

    if not bottlenecks:
        bottlenecks.append("No significant bottlenecks detected")

    return bottlenecks


def generate_proactive_suggestions(goals, task_counts, revenue):
    """
    Generate proactive business suggestions based on data analysis.

    Args:
        goals: Business goals dictionary
        task_counts: Task completion counts
        revenue: Calculated revenue

    Returns:
        list: List of actionable suggestions
    """
    suggestions = []

    # Revenue-based suggestions
    revenue_gap = goals['monthly_revenue_target'] - revenue
    if revenue_gap > 5000:
        suggestions.append(f"Revenue gap of ${revenue_gap:,} - prioritize high-value client outreach")
        suggestions.append("Consider launching targeted social media campaign to generate leads")

    # Task-based suggestions
    if task_counts['social_media'] < 3:
        suggestions.append("Low social media engagement - increase monitoring frequency or expand keyword list")

    if task_counts['business'] > task_counts['personal'] * 3:
        suggestions.append("Work-life balance alert - schedule personal time to prevent burnout")

    # Project-based suggestions
    if goals['active_projects']:
        suggestions.append(f"Track progress on {len(goals['active_projects'])} active projects - schedule status check-ins")

    # General optimization
    suggestions.append("Review Business_Goals.md weekly to ensure targets remain aligned with market conditions")
    suggestions.append("Consider automating recurring tasks to free up strategic thinking time")

    return suggestions


def generate_ceo_briefing():
    """
    Generate the CEO Briefing report and save to /Logs/.
    """
    setup_directories()

    print("[CEO BRIEFING] Generating CEO Briefing...\n")

    # Gather data
    goals = read_business_goals()
    task_counts = scan_completed_tasks()
    revenue = calculate_mock_revenue(task_counts)
    bottlenecks = identify_bottlenecks()
    suggestions = generate_proactive_suggestions(goals, task_counts, revenue)

    # Calculate metrics
    revenue_target = goals['monthly_revenue_target']
    revenue_percentage = (revenue / revenue_target * 100) if revenue_target > 0 else 0
    revenue_status = "[ON TRACK]" if revenue_percentage >= 80 else "[NEEDS ATTENTION]"

    # Generate report
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_filename = f"CEO_Briefing_{date_str}.md"
    report_path = LOGS_DIR / report_filename

    report_content = f"""# CEO Executive Briefing
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Period:** Week of {date_str}

---

## Executive Summary

The AI Employee Vault processed **{task_counts['total']} tasks** this period, generating an estimated **${revenue:,}** in business value. Current performance is at **{revenue_percentage:.1f}%** of monthly revenue target.

**Status:** {revenue_status}

---

## Revenue vs. Target

| Metric | Value | Target | Performance |
|--------|-------|--------|-------------|
| **Estimated Revenue** | ${revenue:,} | ${revenue_target:,} | {revenue_percentage:.1f}% |
| **Revenue Gap** | ${revenue_target - revenue:,} | - | - |
| **Days Remaining** | {30 - datetime.now().day} | - | - |

### Revenue Breakdown by Source
- Business Tasks: ${task_counts['business'] * 500:,} ({task_counts['business']} tasks × $500)
- Social Media Leads: ${task_counts['social_media'] * 200:,} ({task_counts['social_media']} leads × $200)
- Email Management: ${task_counts['emails'] * 100:,} ({task_counts['emails']} emails × $100)

---

## Completed Tasks

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Tasks** | {task_counts['total']} | 100% |
| Business | {task_counts['business']} | {(task_counts['business']/task_counts['total']*100) if task_counts['total'] > 0 else 0:.1f}% |
| Social Media | {task_counts['social_media']} | {(task_counts['social_media']/task_counts['total']*100) if task_counts['total'] > 0 else 0:.1f}% |
| Emails | {task_counts['emails']} | {(task_counts['emails']/task_counts['total']*100) if task_counts['total'] > 0 else 0:.1f}% |
| Personal | {task_counts['personal']} | {(task_counts['personal']/task_counts['total']*100) if task_counts['total'] > 0 else 0:.1f}% |
| Documents | {task_counts['documents']} | {(task_counts['documents']/task_counts['total']*100) if task_counts['total'] > 0 else 0:.1f}% |

---

## Bottlenecks & Risks

"""

    for bottleneck in bottlenecks:
        report_content += f"- {bottleneck}\n"

    report_content += f"""
---

## Proactive Suggestions

"""

    for i, suggestion in enumerate(suggestions, 1):
        report_content += f"{i}. {suggestion}\n"

    report_content += f"""
---

## Active Projects

"""

    if goals['active_projects']:
        for project in goals['active_projects']:
            report_content += f"- **{project['name']}** - Due: {project['due']}\n"
    else:
        report_content += "- No active projects tracked in Business_Goals.md\n"

    report_content += f"""
---

## Next Steps

1. Review and address identified bottlenecks
2. Implement top 3 proactive suggestions
3. Update Business_Goals.md with current progress
4. Schedule client outreach for revenue gap closure
5. Run 'Process tasks' to clear pending queue

---

*Auto-generated by Weekly Auditor - Gold Tier Business Intelligence*
"""

    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"[SUCCESS] CEO Briefing generated: {report_filename}")
    print(f"  Location: {report_path}")
    print(f"\n[METRICS] Key Metrics:")
    print(f"  Revenue: ${revenue:,} / ${revenue_target:,} ({revenue_percentage:.1f}%)")
    print(f"  Tasks Completed: {task_counts['total']}")
    print(f"  Bottlenecks: {len(bottlenecks)}")
    print(f"  Suggestions: {len(suggestions)}")


if __name__ == '__main__':
    generate_ceo_briefing()
