# Resume Document PDF Generator

A Python GUI application that generates professional resumes in DOCX and PDF formats by combining base information with ChatGPT-formatted resume content.

## Features

- 🖥️ **User-friendly GUI** - Simple two-tab interface for data entry
- 📝 **ChatGPT Integration** - Paste ChatGPT-formatted resume output directly
- 🏢 **Multi-Company Support** - Generate resumes tailored for different companies
- 📄 **DOCX & PDF Export** - Automatically generates both formats
- 💾 **Config Save/Load** - Save and reuse your resume configurations
- 🔄 **Template-Based** - Uses customizable DOCX templates with tag replacement

## Requirements

### Python
- Python 3.7 or higher

### External Tools
- **WinRAR** (required) - For creating DOCX files
  - Download from: https://www.winrar.com/
  - Install to default location: `C:\Program Files\WinRAR\` or `C:\Program Files (x86)\WinRAR\`

- **PDF Converter** (optional, choose one):
  - **PyPandoc** (requires pandoc + LaTeX)
    - Install: `pip install pypandoc`
  - **docx2pdf** (Windows-only, requires Microsoft Word)
    - Install: `pip install docx2pdf`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-doc-pdf-gen
   ```

2. **Install optional dependencies** (for PDF conversion)
   ```bash
   pip install -r requirement.txt
   ```
   
   Or install individually:
   ```bash
   pip install pypandoc
   # OR
   pip install docx2pdf
   ```

3. **Install external tools**
   - Install WinRAR (required)

4. **Prepare your template**
   - Extract your DOCX template to `input/template1/`
   - The template should contain tags like:
     - `<resume_person_name>`
     - `<resume_person_email>`
     - `<resume_company_name>`
     - `<resume_company_role>`
     - `<resume_company_bullet>`
     - `<resume_skill_head>`
     - `<resume_skill_body>`
     - And more...

## Usage

### Launch the Application

```bash
python main.py
```

### Using the GUI

1. **Base Information Tab**
   - Fill in personal information (name, location, email, phone, LinkedIn)
   - Enter education details (university, location, graduation date)
   - List companies (comma-separated) for which you want to generate resumes

2. **ChatGPT Input Tab**
   - Enter output folder name (e.g., "Amazon+Software Engineer")
   - Paste your ChatGPT-formatted resume output
   - Format should include:
     - PROFESSIONAL SUMMARY
     - SKILLS
     - EXPERIENCE (with company names matching your list)

3. **Generate Resume**
   - Click "🚀 Generate Resume" button
   - Files will be saved to `output/[folder_name]/`
   - PDF will automatically open if conversion succeeds

### Config Management

- **Save Config**: Save your current settings to a JSON file
- **Load Config**: Load previously saved settings

### File Structure

```
resume-doc-pdf-gen/
├── main.py                 # Application entry point
├── gui.py                  # GUI interface
├── processor.py            # Core processing logic
├── parser.py               # ChatGPT output parser
├── pdf_converter.py        # PDF conversion utilities
├── input/
│   ├── template1/         # DOCX template (extract here)
│   ├── base_data.json      # Base data (auto-generated)
│   ├── chatgpt.txt         # ChatGPT output (auto-generated)
│   └── company.txt         # Company tracking (auto-generated)
└── output/
    └── [folder_name]/      # Generated resumes
        ├── resume.docx
        └── resume.pdf
```

## ChatGPT Output Format

The application expects ChatGPT output in this format:

```
PROFESSIONAL SUMMARY
Your professional summary text here.

SKILLS
Technical: Python, Java, Spring Boot, AWS
Soft: Leadership, Communication

EXPERIENCE
Company Name | Date Range | Role Title | Location
• First achievement or responsibility
• Second achievement or responsibility
• Third achievement or responsibility

Another Company | Date Range | Role Title | Location
• Achievement 1
• Achievement 2
```

## Template Tags

Your DOCX template should use these tags for automatic replacement:

### Personal Information
- `<resume_person_name>` - Full name
- `<resume_person_location>` - Location
- `<resume_person_email>` - Email address
- `<resume_person_linkedin>` - LinkedIn URL

### Education
- `<resume_education_name>` - University name
- `<resume_education_location>` - University location
- `<resume_education_date>` - Graduation date

### Professional Summary
- `<resume_summary>` - Professional summary text

### Experience (Company Block)
- `<resume_company_name>` - Company name
- `<resume_company_role>` - Job title
- `<resume_company_location>` - Job location
- `<resume_company_dates>` - Employment dates
- `<resume_company_bullet>` - Bullet point (will be repeated for each bullet)

### Skills
- `<resume_skill_head>` - Skill category name
- `<resume_skill_body>` - Skill list

## Troubleshooting

### WinRAR Not Found
- Ensure WinRAR is installed to one of the default locations
- The application checks:
  - `C:\Program Files\WinRAR\WinRAR.exe`
  - `C:\Program Files (x86)\WinRAR\WinRAR.exe`

### PDF Conversion Fails
- Install one of the Python PDF libraries
- Check that the DOCX file was created successfully first

### Template Not Found
- Extract your DOCX file to `input/template1/`
- Ensure `input/template1/word/document.xml` exists

### Company Duplication Error
- The app prevents generating resumes for the same company twice
- Check `input/company.txt` to see tracked companies
- Use a different folder name or modify the company list

## License

Under MIT3.0 License

## Contributing

[Victor Anderson]

