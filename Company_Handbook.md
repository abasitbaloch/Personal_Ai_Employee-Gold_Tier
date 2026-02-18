# AI Employee Vault - Standard Operating Procedures (Silver Tier)

## 🛡️ Core Operational Directives (CRITICAL)

**Execute and Terminate:** Never loop. Process the active tasks in your queue, move the files to their final destinations, update the logs/dashboard, and IMMEDIATELY STOP.

**State Management:** Only process files actively residing in /Needs_Action, /Pending_Approval, or /Approved. Do NOT scan /Done or /Logs.

## 🥉 Bronze Tier Skills (Basic Triage)

**Trigger:** User says "Process tasks"

**Local Files (ALERT_*.md):** Read the alert and the dropped file. Move both to the appropriate smart subfolder in /Done. Update Dashboard.md and log the action. STOP.

**Emails (EMAIL_*.md):** Read the email content. Route it to the appropriate subfolder in /Done. Update Dashboard.md and log the action. STOP.

## 🥈 Silver Tier Skills (Advanced Logic & HITL)

**Trigger:** User says "Process tasks"

**Scheduled Tasks (FILE_test_schedule.md or FILE_morning_briefing.md):** Write a 'Good Morning' status in today's log, move the trigger file to /Done/Documents, update Dashboard.md, and STOP.

**Complex Actions (e.g., Social Media / LinkedIn):**
1. Write a step-by-step checklist in /Plans.
2. Generate the highly engaging professional content.
3. Save the final draft to /Pending_Approval (This is the HITL Safety Gate).
4. Move the original request file to /Done/Documents.
5. Update Dashboard.md, log the action, and STOP.

## 🚀 Execution Skill (External Actions)

**Trigger:** User says "Execute approved"

**Action:** Check /Approved. For any approved draft, execute the corresponding external tool (e.g., run python Scripts/linkedin_automation.py <file_path>).

**Cleanup:** Upon successful execution, move the executed draft to /Done/Documents, log the success, update Dashboard.md, and STOP.

## 🥇 Gold Tier Skills (Business Intelligence & Cross-Domain Integration)

**Trigger:** User says "Process tasks"

**Cross-Domain Integrator (ALWAYS RUN FIRST):**
1. Before processing any tasks, run: `python Scripts/cross_domain_integrator.py`
2. This script automatically categorizes all .md files in /Needs_Action into:
   - /Needs_Action/Business/ (client work, revenue, projects, professional tasks)
   - /Needs_Action/Personal/ (family, health, hobbies, personal appointments)
3. After categorization completes, proceed with normal task processing from the categorized subfolders.

**Business Goals Monitoring:**
- Reference /Vault/Business_Goals.md for revenue targets, key metrics, and active projects.
- When processing business tasks, check if they relate to tracked metrics or active projects.
- Flag alerts if thresholds are exceeded (e.g., client response time > 48 hours, costs > $600/month).
- Update business metrics in Dashboard.md when relevant data is processed.

**Social Media Empire (Automated Client Capture):**

**Background Watcher:**
- Run `python social_media_watcher.py` in a separate terminal to monitor Facebook messages 24/7.
- The watcher automatically scans for business keywords: 'client', 'urgent', 'sale', 'project', 'pricing'.
- Creates SOCIAL_MSG_<timestamp>.md files in /Needs_Action/Business/ for every matching message.
- Uses persistent browser session (saved in /user_data/social_session) - only requires manual login once.

**Trigger:** User says "Process social"

**Social Message Processing:**
1. Run: `python Scripts/social_summary_generator.py`
2. Script scans /Needs_Action/Business/ for all SOCIAL_MSG_*.md files.
3. For each message, generates a highly professional draft reply tailored to landing the client.
4. Saves draft to /Pending_Approval/ (enforcing HITL safety gate).
5. Moves original SOCIAL_MSG_ file to /Done/Data/.
6. Update Dashboard.md with social media activity metrics.
7. STOP.

**Weekly Audit (CEO Briefing Generator):**

**Trigger:** User says "Generate briefing"

**Action:**
1. Run: `python Scripts/weekly_auditor.py`
2. Script reads Business_Goals.md to understand revenue targets and objectives.
3. Scans /Done/ and /Logs/ folders to calculate total revenue and completed task counts.
4. Generates a professional CEO_Briefing_<date>.md report in /Logs/ folder.
5. Report includes: Executive Summary, Revenue vs. Target, Completed Tasks, Bottlenecks, and Proactive Suggestions.
6. STOP.

**Master Orchestrator (Ralph Wiggum Loop - True Autonomy):**

**Trigger:** User says "Run orchestrator"

**Action:**
1. Run: `python orchestrator_loop.py`
2. Enters continuous autonomous operation mode with while True loop.
3. Monitors /Needs_Action/ and all subfolders for pending tasks.
4. When tasks detected: automatically executes cross_domain_integrator.py, then social_summary_generator.py.
5. When queue empty: prints "Ralph Wiggum hook activated. Waiting for new tasks..." and sleeps 30 seconds.
6. Continues until manually stopped with Ctrl+C.
7. This ensures the AI keeps working until all folders are perfectly clean.

**Note:** The orchestrator represents true autonomous operation - the AI employee works continuously without human intervention until all tasks are processed.

**Execution Order:**
1. Run Cross-Domain Integrator first
2. Process Business tasks from /Needs_Action/Business/
3. Process Personal tasks from /Needs_Action/Personal/
4. Update Dashboard.md with categorized metrics
5. STOP
