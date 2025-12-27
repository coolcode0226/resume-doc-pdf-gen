"""
Parse ChatGPT output into structured data
"""

import json


def parse_chatgpt_output(text, input_data=None):
    
    lines = [line.strip() for line in text.strip().split('\n')]
    
    # Initialize data structure
    data = {
        'personal': {},
        'summary': '',
        'skills': {},
        'experiences': [],
        'education': {}
    }

    data['education'] = input_data.get('education', {}) if input_data else {}
    
    # Parse personal info (pipe-separated format)
    # Collect all pipe-separated values from initial lines until we hit empty lines
    personal_parts = []
    for line in lines:
        if not line:  # Stop at first empty line
            break
        personal_parts.extend([p.strip() for p in line.split('|')])
    
    # Filter out empty parts
    personal_parts = [p for p in personal_parts if p]
    
    personal_info = {}
    remaining_parts = []
    
    # Intelligently classify each part
    for part in personal_parts:
        if '@' in part:
            personal_info['email'] = part
        elif 'linkedin.com' in part.lower():
            personal_info['linkedin'] = part
        elif any(char.isdigit() for char in part) and ('+' in part or '-' in part or ' ' in part or part[0].isdigit()):
            # Looks like a phone number (contains digits and phone separators)
            personal_info['phone'] = part
        else:
            remaining_parts.append(part)
    
    # Assign remaining parts: first is name, second is location
    if len(remaining_parts) >= 1:
        personal_info['name'] = remaining_parts[0]
    if len(remaining_parts) >= 2:
        personal_info['location'] = remaining_parts[1]
    
    data['personal'] = personal_info
    
    # Find summary section
    summary_start = -1
    for i, line in enumerate(lines):
        if 'PROFESSIONAL SUMMARY' in line.upper():
            summary_start = i + 1
            break
    
    if summary_start != -1:
        # Find where summary ends (next section)
        summary_lines = []
        started = False
        for line in lines[summary_start:]:
            # Skip empty lines until we find actual content
            if not line:
                if started:
                    break
                continue
            # Stop at next section header
            summary_lines.append(line)
            started = True
            if 'SKILLS' in line.upper():
                break
        data['summary'] = ' '.join(summary_lines)
    
    # Find skills section
    skills_start = -1
    for i, line in enumerate(lines):
        if 'SKILLS' in line.upper():
            skills_start = i + 1
            break
    
    if skills_start != -1:
        # Parse all skill lines until next section
        for line in lines[skills_start:]:
            if not line:
                continue
            if 'PROFESSIONAL EXPERIENCE' in line.upper() or 'EXPERIENCE' in line.upper():
                break
            if ':' in line:
                parts = line.split(':', 1)
                category = parts[0].strip()
                skills_list = parts[1].strip()
                if len(skills_list) < 5:
                    continue
                data['skills'][category] = skills_list
    
    # Find experiences (search after skills section)
    experience_start = -1
    search_start = skills_start if skills_start != -1 else 0
    for i, line in enumerate(lines[search_start:], start=search_start):
        if 'PROFESSIONAL EXPERIENCE' in line.upper() or ('EXPERIENCE' in line.upper() and 'PROFESSIONAL' in line.upper()):
            experience_start = i + 1
            break
    
    if experience_start != -1:
        # Get company list from input_data if provided
        companies_to_extract = []
        companies_to_extract = input_data.get('company', []) if input_data else []
        
        current_exp = None
        current_company = None
        empty_line_count = 0
        
        for line in lines[experience_start:]:
            # Check if we've reached the Education section
            if 5 <= len(line.strip()) <= 30:
                # End of experience section
                if current_exp and current_exp['bullets']:
                    data['experiences'].append(current_exp)
                break
            
            # Track consecutive empty lines
            if not line:
                empty_line_count += 1
                continue
            
            # Check if line contains a company name from our list
            is_company_line = False
            for company in companies_to_extract:
                if company.lower() in line.lower():
                    if current_exp != None:
                        if current_exp['company'] == company:
                            is_company_line = False
                        else:
                            is_company_line = True
                            current_company = company
                            break
                    else:
                        is_company_line = True
                        current_company = company
                        break
            
            # If we found a company name, save previous experience and start new one
            if is_company_line:
                if current_exp and current_exp['bullets']:
                    data['experiences'].append(current_exp)
                
                # Parse the company line: Company | Dates | Role | Location
                parts = [p.strip() for p in line.split('|')]
                current_exp = {
                    'company': current_company,
                    'dates': parts[1] if len(parts) > 1 else '',
                    'role': parts[2] if len(parts) > 2 else '',
                    'location': parts[3] if len(parts) > 3 else '',
                    'bullets': []
                }
                empty_line_count = 0
            
            # Check if we're transitioning to a new section (multiple empty lines before non-company, non-bullet line)
            elif empty_line_count > 1 and current_exp and line and not line[0].isalpha() and not any(company.lower() in line.lower() for company in companies_to_extract):
                # This might be end of experiences section, save and stop
                if current_exp['bullets']:
                    data['experiences'].append(current_exp)
                    current_exp = None
                break
            
            # Add any non-empty, non-company line as a bullet point
            elif current_exp and line:
                # Remove leading bullet character if it exists (•, -, *, +, etc.)
                # If no symbol, use the line as-is
                bullet_text = line.strip()
                if bullet_text and bullet_text[0] in '•-*+':
                    bullet_text = bullet_text[1:].strip()
                
                # Add as bullet point (works with or without symbols)
                if bullet_text:
                    current_exp['bullets'].append(bullet_text)
                
                empty_line_count = 0
    
    return data