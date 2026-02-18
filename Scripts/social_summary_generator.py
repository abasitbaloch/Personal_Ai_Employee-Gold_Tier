#!/usr/bin/env python3
"""
Social Summary Generator - Gold Tier Skill
Processes social media messages and generates professional draft replies.
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Paths
VAULT_ROOT = Path(__file__).parent.parent
NEEDS_ACTION_BUSINESS = VAULT_ROOT / 'Needs_Action' / 'Business'
PENDING_APPROVAL = VAULT_ROOT / 'Pending_Approval'
DONE_DATA = VAULT_ROOT / 'Done' / 'Data'


def setup_directories():
    """Create necessary directories if they don't exist."""
    PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)
    DONE_DATA.mkdir(parents=True, exist_ok=True)


def extract_message_data(filepath):
    """
    Extract message data from a SOCIAL_MSG markdown file.

    Args:
        filepath: Path to the SOCIAL_MSG_*.md file

    Returns:
        dict: Extracted message data (platform, sender, timestamp, content)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract fields using regex
    platform_match = re.search(r'\*\*Platform:\*\* (.+)', content)
    sender_match = re.search(r'\*\*Sender:\*\* (.+)', content)
    timestamp_match = re.search(r'\*\*Received:\*\* (.+)', content)

    # Extract message content (everything after "## Message Content")
    message_match = re.search(r'## Message Content\n\n(.+?)\n\n---', content, re.DOTALL)

    return {
        'platform': platform_match.group(1) if platform_match else 'Unknown',
        'sender': sender_match.group(1) if sender_match else 'Unknown',
        'timestamp': timestamp_match.group(1) if timestamp_match else 'Unknown',
        'message': message_match.group(1).strip() if message_match else content
    }


def generate_professional_reply(message_data):
    """
    Generate a highly professional draft reply tailored to landing a client.
    Supports SOCIAL_MSG, TWITTER_MSG, and WHATSAPP_MSG platforms.

    Args:
        message_data: Dictionary containing message information

    Returns:
        str: Professional draft reply
    """
    message_lower = message_data['message'].lower()
    sender = message_data['sender']
    platform = message_data.get('platform', 'Unknown')

    # Analyze message intent and craft appropriate response
    if 'urgent' in message_lower or 'asap' in message_lower:
        reply = f"""Hi {sender},

Thank you for reaching out. I understand this is time-sensitive, and I'm prioritizing your request immediately.

I'm available to discuss this right away. Would you prefer a quick call, or should I provide a detailed response here?

Looking forward to helping you resolve this quickly.

Best regards"""

    elif 'pricing' in message_lower or 'quote' in message_lower:
        reply = f"""Hi {sender},

Thank you for your interest! I'd be happy to provide you with a detailed pricing proposal.

To ensure I give you the most accurate quote, could you share a few quick details:
• Project scope and timeline
• Any specific requirements or deliverables
• Your preferred budget range (if any)

I typically respond with custom proposals within 24 hours. Would you like to schedule a brief call to discuss this in more detail?

Best regards"""

    elif 'project' in message_lower:
        reply = f"""Hi {sender},

Thank you for considering me for your project! I'm excited about the opportunity to work together.

I'd love to learn more about:
• Your project goals and vision
• Timeline and key milestones
• Budget and resource requirements

I have availability this week for a discovery call. What works best for your schedule?

Looking forward to collaborating with you.

Best regards"""

    elif 'client' in message_lower or 'sale' in message_lower:
        reply = f"""Hi {sender},

Thank you for reaching out! I appreciate you thinking of me for this opportunity.

I'd be delighted to discuss how I can help. Could you share more details about what you're looking for? I want to ensure I provide the best possible solution for your needs.

I'm available for a call or video meeting at your convenience. What time works best for you?

Best regards"""

    elif 'invoice' in message_lower or 'payment' in message_lower:
        reply = f"""Hi {sender},

Thank you for your message regarding the invoice/payment.

I'm reviewing this immediately and will provide you with the necessary information or resolution within the next few hours.

If this is time-sensitive, please let me know and I'll prioritize it accordingly.

Best regards"""

    elif 'help' in message_lower:
        reply = f"""Hi {sender},

Thank you for reaching out. I'm here to help!

Could you provide more details about what you need assistance with? I want to make sure I address your concerns thoroughly.

I'm available to discuss this right away if needed.

Best regards"""

    else:
        # Generic professional response
        reply = f"""Hi {sender},

Thank you for your message! I appreciate you reaching out.

I'd be happy to discuss this further and explore how I can help. Could you provide a bit more context about your needs and timeline?

I'm available for a call or meeting at your convenience. Looking forward to connecting.

Best regards"""

    return reply


def process_social_messages():
    """
    Main function to process all SOCIAL_MSG, TWITTER_MSG, and WHATSAPP_MSG files and generate draft replies.
    """
    setup_directories()

    # Find all social media message files (SOCIAL_MSG, TWITTER_MSG, WHATSAPP_MSG)
    social_msg_files = []
    social_msg_files.extend(NEEDS_ACTION_BUSINESS.glob('SOCIAL_MSG_*.md'))
    social_msg_files.extend(NEEDS_ACTION_BUSINESS.glob('TWITTER_MSG_*.md'))
    social_msg_files.extend(NEEDS_ACTION_BUSINESS.glob('WHATSAPP_MSG_*.md'))

    if not social_msg_files:
        print("No social media messages to process.")
        return

    print(f"[SOCIAL] Processing {len(social_msg_files)} social media message(s)...\n")

    for msg_file in social_msg_files:
        try:
            print(f"Processing: {msg_file.name}")

            # Extract message data
            message_data = extract_message_data(msg_file)

            # Generate professional reply
            draft_reply = generate_professional_reply(message_data)

            # Create draft file in Pending_Approval
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            draft_filename = f"DRAFT_REPLY_{timestamp}.md"
            draft_filepath = PENDING_APPROVAL / draft_filename

            draft_content = f"""# Draft Reply - Pending Approval

**Original Message From:** {message_data['sender']}
**Platform:** {message_data['platform']}
**Received:** {message_data['timestamp']}

## Original Message

{message_data['message']}

---

## Proposed Reply (REVIEW BEFORE SENDING)

{draft_reply}

---

**Instructions:**
1. Review and edit the reply above as needed
2. Once approved, move this file to /Approved
3. The AI will then execute the send action

*Auto-generated by Social Summary Generator*
"""

            with open(draft_filepath, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            print(f"  [SUCCESS] Draft created: {draft_filename}")

            # Move original message to Done/Data
            dest_path = DONE_DATA / msg_file.name
            msg_file.rename(dest_path)
            print(f"  [SUCCESS] Original moved to: Done/Data/{msg_file.name}\n")

        except Exception as e:
            print(f"  [ERROR] Error processing {msg_file.name}: {e}\n")

    print(f"[SUCCESS] Social message processing complete!")
    print(f"  {len(social_msg_files)} draft(s) awaiting approval in /Pending_Approval")


if __name__ == '__main__':
    process_social_messages()
