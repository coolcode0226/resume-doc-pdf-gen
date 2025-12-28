"""
Core resume processor - Cleaned Version
"""
import subprocess
import os
import shutil
import re
import tempfile
from parser import parse_chatgpt_output


class ResumeProcessor:
    """Processes resume templates by replacing tags with actual data."""
    
    # XML special character escaping map
    XML_ESCAPES = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    }
    
    # WinRAR executable paths
    WINRAR_PATHS = [
        r"C:\Program Files\WinRAR\WinRAR.exe",
        r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
    ]

    def __init__(self, template_doc, template_folder, chatgpt_text, config=None):
        """Initialize the resume processor."""
        self.template_doc = template_doc
        self.template_folder = template_folder
        self.chatgpt_text = chatgpt_text
        self.xml_content = ''
        self.parsed_data = {}
        self.config = config
        self.temp_working_folder = None
        self.base_data = {}

    def run(self):
        """Main processing pipeline."""
        try:
            self._load_files()
            self._validate_data()
            self._process_xml()
            self._save_output()
            self._create_working_copy()
            return self._create_docx_from_folder()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def _load_files(self):
        """Load input files and parse data."""
        # Load XML template
        with open(self.template_doc, 'r', encoding='utf-8') as f:
            self.xml_content = f.read()
        
        # Prepare base data structure
        self.base_data = {
            'personal': {},
            'company': ["Microsoft", "PayPal", "Tagani"],
            'education': [],  # Changed to list
        }

        print(self.config)


        self.base_data['company'] = self.config.get('company', ["Microsoft", "PayPal", "Tagani"])
        personal_info = {}

        self.base_data['personal'] = self.config.get('personal', {})

        # Handle education as list (backward compatible with dict)
        education_data = self.config.get('education', [])
        if isinstance(education_data, dict):
            # Convert old format to list
            education_data = [education_data]
        elif not isinstance(education_data, list):
            education_data = []
        self.base_data['education'] = education_data

        # Parse data
        self.parsed_data = parse_chatgpt_output(self.chatgpt_text, self.base_data)
        
        print(self.parsed_data)
        print("✓ Files loaded and parsed successfully")

    def _validate_data(self):
        """Validate parsed data."""
        if not self.parsed_data.get('personal'):
            raise ValueError("No personal information found")
        
        if not self.parsed_data.get('experiences'):
            raise ValueError("No experiences found")
        
        exp_count = len(self.parsed_data['experiences'])
        print(f"✓ Parsed {exp_count} experiences")
        
        for exp in self.parsed_data['experiences']:
            print(f"  - {exp['company']}: {len(exp['bullets'])} bullet points")

    def _process_xml(self):
        """Process XML content by replacing tags."""
        self._replace_simple_tags()
        self._process_company_block()
        self._process_education_block()
        self._process_skill_block()
        self._check_remaining_tags()

    def _replace_simple_tags(self):
        """Replace simple one-to-one tags."""
        # Get first education entry (for backward compatibility)
        first_education = {}
        if self.base_data['education'] and len(self.base_data['education']) > 0:
            first_education = self.base_data['education'][0]
        
        replacements = {
            '<resume_person_name>': self.base_data['personal'].get('name', ''),
            '<resume_person_location>': self.base_data['personal'].get('location', ''),
            '<resume_person_email>': self.base_data['personal'].get('email', ''),
            '<resume_person_linkedin>': self.base_data['personal'].get('linkedin', ''),
            '<resume_summary>': self.parsed_data.get('summary', ''),
            '<resume_education_name>': first_education.get('university', ''),
            '<resume_education_location>': first_education.get('edu_location', ''),
            '<resume_education_date>': first_education.get('graduation_year', '')
        }
        
        for tag, value in replacements.items():
            if tag in self.xml_content:
                self.xml_content = self.xml_content.replace(tag, self._escape_xml(value))
                print(f"✓ Replaced {tag}")
            else:
                print(f"⚠ Tag not found: {tag}")
        
        # Process multiple education entries if there are more than one
        if len(self.base_data['education']) > 1:
            self._process_education_block()

    def _process_company_block(self):
        """Find and replace the company block template."""
        block_info = self._find_company_block()
        if not block_info:
            raise ValueError("Could not find company block in template")
        
        start_idx, end_idx, block_template = block_info
        
        # Generate company blocks
        company_blocks = [
            self._create_company_xml(block_template, exp)
            for exp in self.parsed_data['experiences']
        ]
        
        # Replace in XML
        self.xml_content = (
            self.xml_content[:start_idx] +
            '\n'.join(company_blocks) +
            self.xml_content[end_idx:]
        )
        
        print(f"✓ Replaced company block with {len(company_blocks)} companies")

    def _find_company_block(self):
        """Find the company block template in XML."""
        role_tag = '<resume_company_role>'
        role_pos = self.xml_content.find(role_tag)
        
        if role_pos == -1:
            return None
        
        # Find paragraph start
        para_start = self.xml_content.rfind('<w:p w14', 0, role_pos)
        if para_start == -1:
            return None
        
        # Find "EDUCATION" section
        education_pos = self.xml_content.lower().find('education', role_pos)
        if education_pos == -1:
            return None
        
        # Find paragraph containing "EDUCATION"
        education_para_start = self.xml_content.rfind('<w:p w14', 0, education_pos)
        if education_para_start == -1:
            return None
        
        # Find block end (paragraph before "EDUCATION")
        block_end = self.xml_content.rfind('</w:p>', 0, education_para_start)
        if block_end == -1:
            return None
        
        block_end += 6  # Include "</w:p>"
        
        return (para_start, block_end, self.xml_content[para_start:block_end])

    def _create_company_xml(self, template, experience):
        """Create XML for a single company from template."""
        # Basic replacements
        replacements = {
            '<resume_company_name>': experience['company'],
            '<resume_company_role>': experience['role'],
            '<resume_company_location>': experience['location'],
            '<resume_company_dates>': experience['dates']
        }
        
        company_xml = template
        for tag, value in replacements.items():
            if tag in company_xml:
                company_xml = company_xml.replace(tag, self._escape_xml(value))
        
        # Handle bullet points
        bullet_para = self._extract_bullet_paragraph(company_xml)
        if bullet_para and experience['bullets']:
            bullet_xmls = [
                bullet_para.replace('<resume_company_bullet>', self._escape_xml(bullet))
                for bullet in experience['bullets']
            ]
            company_xml = company_xml.replace(bullet_para, '\n'.join(bullet_xmls))
        
        return company_xml

    def _extract_bullet_paragraph(self, xml_text):
        """Extract the paragraph containing bullet tag."""
        bullet_tag = '<resume_company_bullet>'
        bullet_pos = xml_text.find(bullet_tag)
        
        if bullet_pos == -1:
            return None
        
        # Find paragraph boundaries
        para_start = xml_text.rfind('<w:p w14', 0, bullet_pos)
        para_end = xml_text.find('</w:p>', bullet_pos)
        
        if para_start == -1 or para_end == -1:
            return None
        
        para_end += 6  # Include "</w:p>"
        return xml_text[para_start:para_end]

    def _process_education_block(self):
        """Find and replace the education block template for multiple entries."""
        # Only process if we have more than one education entry
        if len(self.base_data['education']) <= 1:
            return
        
        block_info = self._find_education_block()
        if not block_info:
            print("⚠ Could not find education block template, using first entry only")
            return
        
        start_idx, end_idx, block_template = block_info
        
        # Generate education blocks (skip first as it's already replaced)
        education_blocks = [
            self._create_education_xml(block_template, edu)
            for edu in self.base_data['education'][1:]  # Skip first entry
        ]
        
        # Replace in XML (insert after first education entry)
        self.xml_content = (
            self.xml_content[:end_idx] +
            '\n'.join(education_blocks) +
            self.xml_content[end_idx:]
        )
        
        print(f"✓ Added {len(education_blocks)} additional education entries")
    
    def _find_education_block(self):
        """Find the education block template in XML."""
        name_tag = '<resume_education_name>'
        name_pos = self.xml_content.find(name_tag)
        
        if name_pos == -1:
            return None
        
        # Find paragraph start
        para_start = self.xml_content.rfind('<w:p w14', 0, name_pos)
        if para_start == -1:
            return None
        
        # Find paragraph end
        para_end = self.xml_content.find('</w:p>', name_pos)
        if para_end == -1:
            return None
        
        para_end += 6  # Include "</w:p>"
        
        return (para_start, para_end, self.xml_content[para_start:para_end])
    
    def _create_education_xml(self, template, education):
        """Create XML for a single education entry from template."""
        replacements = {
            '<resume_education_name>': education.get('university', ''),
            '<resume_education_location>': education.get('edu_location', ''),
            '<resume_education_date>': education.get('graduation_year', '')
        }
        
        education_xml = template
        for tag, value in replacements.items():
            if tag in education_xml:
                education_xml = education_xml.replace(tag, self._escape_xml(value))
        
        return education_xml
    
    def _process_skill_block(self):
        """Find and replace the skill block template."""
        block_info = self._find_skill_block()
        if not block_info:
            raise ValueError("Could not find skill block in template")
        
        start_idx, end_idx, block_template = block_info

        start_idx_last, end_idx_last, block_template_last = self._find_skill_block_last()
        
        # Generate skill blocks
        skill_blocks = []
        skills = self.parsed_data.get('skills', {})
        length = 0
        for category, skill_list in skills.items():
            if length == skills.items().__len__() -1:
                block_template = block_template_last
            skill_xml = block_template.replace(
                '<resume_skill_head>', self._escape_xml(category)
            ).replace(
                '<resume_skill_body>', self._escape_xml(skill_list)
            )
            skill_blocks.append(skill_xml)
            length += 1
        
        # Replace in XML
        self.xml_content = (
            self.xml_content[:start_idx] +
            '\n'.join(skill_blocks) +
            self.xml_content[end_idx:]
        )
        
        print(f"✓ Replaced skill block with {len(skill_blocks)} categories")

    def _find_skill_block(self):
        """Find the skill block template in XML."""
        head_tag = '<resume_skill_head>'
        head_pos = self.xml_content.find(head_tag)
        
        if head_pos == -1:
            return None
        
        # Find start
        block_start = self.xml_content.rfind('<w:r w', 0, head_pos)
        if block_start == -1:
            return None
        
        # Find body tag
        body_tag = '<resume_skill_body>'
        body_pos = self.xml_content.find(body_tag, head_pos)
        if body_pos == -1:
            return None
        
        # Find end
        para_end = self.xml_content.find('</w:r>', body_pos)
        if para_end == -1:
            return None
        
        # Move to next closing tag
        next_para_end = self.xml_content.find('</w:r>', para_end + 1)
        if next_para_end == -1:
            return None
        
        block_end = next_para_end + 6  # Include "</w:r>"
        
        return (block_start, block_end, self.xml_content[block_start:block_end])
    

    def _find_skill_block_last(self):
        """Find the skill block template in XML."""
        head_tag = '<resume_skill_head>'
        head_pos = self.xml_content.find(head_tag)
        
        if head_pos == -1:
            return None
        
        # Find start
        block_start = self.xml_content.rfind('<w:r w', 0, head_pos)
        if block_start == -1:
            return None
        
        # Find body tag
        body_tag = '<resume_skill_body>'
        body_pos = self.xml_content.find(body_tag, head_pos)
        if body_pos == -1:
            return None
        
        # Find end
        para_end = self.xml_content.find('</w:r>', body_pos)
        if para_end == -1:
            return None
        
        block_end = para_end + 6  # Include "</w:r>"
        
        return (block_start, block_end, self.xml_content[block_start:block_end])

    def _escape_xml(self, text):
        """Escape XML special characters."""
        if not text:
            return ""
        
        for char, escape in self.XML_ESCAPES.items():
            text = text.replace(char, escape)
        
        return text

    def _check_remaining_tags(self):
        """Check for any remaining resume tags."""
        remaining_tags = re.findall(r'<resume_[^>]+>', self.xml_content)
        
        if remaining_tags:
            print(f"⚠ {len(remaining_tags)} tags not replaced: {remaining_tags}")
        else:
            print("✓ All tags replaced successfully")

    def _save_output(self):
        """Save processed XML to file."""
        output_path = os.path.join(self.template_folder, "word", "document.xml")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.xml_content)
        
        file_size = os.path.getsize(output_path)
        print(f"✓ Output saved: {output_path} ({file_size:,} bytes)")
        
        return output_path

    def _create_working_copy(self):
        """Create a working copy of the template folder."""
        self.temp_working_folder = tempfile.mkdtemp(prefix="resume_")
        
        print(f"📁 Creating working copy: {self.temp_working_folder}")
        shutil.copytree(
            self.template_folder,
            self.temp_working_folder,
            dirs_exist_ok=True
        )
        
        # Verify document.xml exists
        doc_xml_path = os.path.join(self.temp_working_folder, "word", "document.xml")
        if not os.path.exists(doc_xml_path):
            raise FileNotFoundError(f"document.xml not found in: {doc_xml_path}")
        
        file_count = self._count_files()
        print(f"✓ Created working copy with {file_count} files")

    def _count_files(self):
        """Count files in working folder."""
        return sum(len(files) for _, _, files in os.walk(self.temp_working_folder))

    def _create_docx_from_folder(self):
        """Create DOCX file from the working folder."""
        print("\n📦 Creating DOCX file...")
        
        output_folder_name = self.config.get('folder_name', '').strip() if self.config else ''

        if output_folder_name:
            # Use custom folder name
            output_dir = os.path.join("output", output_folder_name)
            os.makedirs(output_dir, exist_ok=True)
            output_docx = os.path.join(output_dir, "resume.docx")
        
            # Find WinRAR executable
            winrar_path = self._find_winrar()
            if not winrar_path:
                raise RuntimeError("WinRAR not found. Please install WinRAR.")
            
            # Build WinRAR command
            cmd = [
                winrar_path,
                "a",           # Add files to archive
                "-afzip",      # Force ZIP format
                "-ep1",        # Exclude base folder
                "-r",          # Recursive
                "-x*.backup",  # Skip backup files
                output_docx,
                os.path.join(self.temp_working_folder, "*"),
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"WinRAR failed:\n{result.stderr}")
            
            print(f"✓ DOCX created: {output_docx}")
            return output_docx

    def _find_winrar(self):
        """Find WinRAR executable path."""
        for path in self.WINRAR_PATHS:
            if os.path.exists(path):
                return path
        return None
    
    def load_base_data(self):
        """Load base data from JSON file or use defaults"""
        base_data_path = "input/base_data.json"
        
        if os.path.exists(base_data_path):
            try:
                import json
                with open(base_data_path, 'r', encoding='utf-8') as f:
                    self.base_data = json.load(f)
                print(f"✓ Loaded base data from {base_data_path}")
            except Exception as e:
                print(f"⚠ Failed to load base data: {e}")
                self.base_data = self._get_default_base_data()
        else:
            print("⚠ No base_data.json found, using defaults")
            self.base_data = self._get_default_base_data()

    def _get_default_base_data(self):
        """Get default base data"""
        return {
            'personal': {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe"
            },
            'education': {
                "university": "Stanford University",
                "location": "Stanford, CA",
                "graduation_year": "2020"
            },
            'company': ["Microsoft", "PayPal", "Tagani"]
    }