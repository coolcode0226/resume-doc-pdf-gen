#!/usr/bin/env python3
"""
Resume Builder GUI - Simplified Two-Tab Version
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
from pdf_converter import convert_docx_to_pdf
import re

class ResumeBuilderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Resume Builder")
        self.root.geometry("700x600")
        
        # Configure style
        self.setup_styles()
        
        self.education_entries = []
        
        # Create UI
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg='#f0f0f0')
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 14, 'bold'),
                       padding=5)
        style.configure('Field.TLabel',
                       font=('Segoe UI', 10),
                       padding=(0, 5, 5, 0))
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_base_info_tab(notebook)
        self.create_chatgpt_tab(notebook)
        
        # Create bottom buttons
        self.create_generate_buttons()
        
    def create_base_info_tab(self, notebook):
        """Create Base Information tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text='📋 Base Information')
        
        # Config buttons frame (fixed at bottom, centered)
        config_frame = ttk.Frame(frame)
        config_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        # Center the buttons
        button_container = ttk.Frame(config_frame)
        button_container.pack(anchor='center')
        
        ttk.Button(button_container, text="⚙️ Load Base Information",
                  command=self.load_base_information,
                  width=15).pack(side='left', padx=2)
        
        ttk.Button(button_container, text="💾 Save Base Information",
                  command=self.save_base_information,
                  width=15).pack(side='left', padx=2)
        
        # Create scrollable container
        scroll_container = ttk.Frame(frame)
        scroll_container.pack(fill='both', expand=True)

        # Create canvas and scrollbar
        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure canvas window
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Update scroll region and canvas width
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Store reference to scrollable frame
        self.scrollable_frame = scrollable_frame
        
        # Title
        title = ttk.Label(scrollable_frame, text="Base Information", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(20, 10))
        
        # Create form
        self.fields = {}
        current_row = 1
        
        # Personal Information Section
        ttk.Label(scrollable_frame, text="Personal Information", 
                 font=('Segoe UI', 11, 'bold')).grid(
            row=current_row, column=0, columnspan=3, sticky='w', padx=20, pady=(0, 10)
        )
        current_row += 1
        
        # Field definitions for personal info
        personal_fields = [
            ('name', 'Full Name:', 'John Doe', 'personal'),
            ('location', 'Location:', 'San Francisco, CA', 'personal'),
            ('email', 'Email:', 'john.doe@email.com', 'personal'),
            ('phone', 'Phone:', '+1 (555) 123-4567', 'personal'),
            ('linkedin', 'LinkedIn URL:', 'https://linkedin.com/in/johndoe', 'personal')
        ]
        
        for field_key, label_text, placeholder, category in personal_fields:
            label = ttk.Label(scrollable_frame, text=label_text, style='Field.TLabel')
            label.grid(row=current_row, column=0, sticky='w', padx=20, pady=5)
            
            entry = ttk.Entry(scrollable_frame, width=40)
            entry.insert(0, placeholder)
            entry.grid(row=current_row, column=1, sticky='ew', pady=5, padx=(10, 20))
            
            self.fields[field_key] = {
                'entry': entry,
                'category': category
            }
            current_row += 1
        
        # Education Section
        current_row += 1
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=current_row, column=0, columnspan=3, sticky='ew', padx=20, pady=10
        )
        current_row += 1
        
        edu_header_frame = ttk.Frame(scrollable_frame)
        edu_header_frame.grid(row=current_row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 10))
        ttk.Label(edu_header_frame, text="Education", 
                 font=('Segoe UI', 11, 'bold')).pack(side='left')
        ttk.Button(edu_header_frame, text="+ Add Education", 
                  command=self.add_education_entry,
                  width=15).pack(side='right')
        self.edu_start_row = current_row + 1
        
        # Add initial education entries (2 entries)
        for i in range(2):
            self.add_education_entry()
        
        # Calculate row after education entries (each entry takes 5 rows now with degree)
        work_exp_start_row = self.edu_start_row + len(self.education_entries) * 5
        
        # Work Experience Section
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=work_exp_start_row, column=0, columnspan=3, sticky='ew', padx=20, pady=10
        )
        work_exp_start_row += 1
        
        ttk.Label(scrollable_frame, text="Work Experience", 
                 font=('Segoe UI', 11, 'bold')).grid(
            row=work_exp_start_row, column=0, columnspan=3, sticky='w', padx=20, pady=(10, 5)
        )
        work_exp_start_row += 1
        
        # Company field
        label = ttk.Label(scrollable_frame, text='Companies (comma separated):', style='Field.TLabel')
        label.grid(row=work_exp_start_row, column=0, sticky='w', padx=20, pady=5)
        
        entry = ttk.Entry(scrollable_frame, width=40)
        entry.insert(0, 'Microsoft, PayPal, Tagani')
        entry.grid(row=work_exp_start_row, column=1, sticky='ew', pady=5, padx=(10, 20))
        
        self.fields['company'] = {
            'entry': entry,
            'category': 'company'
        }
        
        # Configure grid weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Update canvas scroll region when window is resized
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind('<Configure>', on_frame_configure)
        
    def add_education_entry(self, data=None):
        """Add a new education entry to the form"""
        # Limit to 3 education entries
        if len(self.education_entries) >= 3:
            messagebox.showwarning("Warning", "Maximum 3 education entries allowed")
            return
        
        # Calculate row position (each entry takes 5 rows now with degree)
        row_pos = self.edu_start_row + len(self.education_entries) * 5
        
        # Create entry frame
        entry_frame = ttk.Frame(self.scrollable_frame)
        entry_frame.grid(row=row_pos, column=0, columnspan=3, sticky='ew', pady=5)
        
        # University field
        ttk.Label(entry_frame, text='University:', style='Field.TLabel').grid(row=0, column=0, sticky='w', padx=(20, 5))
        university_entry = ttk.Entry(entry_frame, width=35)
        if data and 'university' in data:
            university_entry.insert(0, data['university'])
        else:
            university_entry.insert(0, 'Stanford University')
        university_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Degree field
        ttk.Label(entry_frame, text='Degree:', style='Field.TLabel').grid(row=1, column=0, sticky='w', padx=(20, 5))
        degree_entry = ttk.Entry(entry_frame, width=35)
        if data and 'degree' in data:
            degree_entry.insert(0, data['degree'])
        else:
            degree_entry.insert(0, 'Bachelor of Science')
        degree_entry.grid(row=1, column=1, sticky='ew', padx=5)
        
        # Location field
        ttk.Label(entry_frame, text='Location:', style='Field.TLabel').grid(row=2, column=0, sticky='w', padx=(20, 5))
        location_entry = ttk.Entry(entry_frame, width=35)
        if data and 'edu_location' in data:
            location_entry.insert(0, data['edu_location'])
        else:
            location_entry.insert(0, 'Stanford, CA')
        location_entry.grid(row=2, column=1, sticky='ew', padx=5)
        
        # Graduation date field
        ttk.Label(entry_frame, text='Graduation Date:', style='Field.TLabel').grid(row=3, column=0, sticky='w', padx=(20, 5))
        graduation_entry = ttk.Entry(entry_frame, width=35)
        if data and 'graduation_year' in data:
            graduation_entry.insert(0, data['graduation_year'])
        else:
            graduation_entry.insert(0, '2020')
        graduation_entry.grid(row=3, column=1, sticky='ew', padx=5)
        
        # Remove button
        entry_data = {
            'frame': entry_frame,
            'university': university_entry,
            'degree': degree_entry,
            'location': location_entry,
            'graduation_year': graduation_entry,
            'row': row_pos
        }
        
        remove_btn = ttk.Button(entry_frame, text="Remove", 
                               command=lambda ed=entry_data: self.remove_education_entry(ed),
                               width=10)
        remove_btn.grid(row=0, column=2, rowspan=4, padx=5)
        
        self.education_entries.append(entry_data)
        entry_frame.columnconfigure(1, weight=1)
    
    def remove_education_entry(self, entry_data):
        """Remove an education entry from the form"""
        if entry_data in self.education_entries:
            entry_data['frame'].destroy()
            self.education_entries.remove(entry_data)
            # Update row positions for remaining entries (each entry takes 5 rows now)
            for i, edu in enumerate(self.education_entries):
                new_row = self.edu_start_row + i * 5
                edu['row'] = new_row
                edu['frame'].grid(row=new_row, column=0, columnspan=3, sticky='ew', pady=5)

    def load_base_information(self):
        """Load Base Information from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Load Base Information",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Load personal data into fields
                for field_key, field_info in self.fields.items():
                    entry = field_info['entry']
                    category = field_info['category']
                    
                    if category == 'company':
                        # Handle company field specially
                        if 'company' in config and config['company']:
                            if isinstance(config['company'], list):
                                company_text = ', '.join(config['company'])
                            else:
                                company_text = str(config['company'])
                            entry.delete(0, tk.END)
                            entry.insert(0, company_text)
                    elif category == 'personal':
                        # Handle personal fields
                        if 'personal' in config and field_key in config['personal']:
                            entry.delete(0, tk.END)
                            entry.insert(0, config['personal'][field_key])
                
                # Load education data (list)
                if 'education' in config:
                    education_data = config['education']
                    # Convert old format (dict) to list if needed
                    if isinstance(education_data, dict):
                        education_data = [education_data]
                    elif not isinstance(education_data, list):
                        education_data = []
                    
                    # Clear existing education entries safely
                    # Destroy all frames first, then clear the list
                    for edu_entry in self.education_entries:
                        edu_entry['frame'].destroy()
                    self.education_entries.clear()
                    
                    # Add loaded education entries
                    for edu_data in education_data:
                        self.add_education_entry(data=edu_data)
                
                messagebox.showinfo("Success", f"Loaded Base Information")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Base Information: {e}")
    
    def save_base_information(self):
        """Save Base Information to JSON file"""
        config = self.collect_base_info()
        
        file_path = filedialog.asksaveasfilename(
            title="Save Base Information",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Base Information saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save Base Information: {e}")
    
    def create_chatgpt_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text='🤖 ChatGPT Input')
        
        # Title
        title = ttk.Label(frame, text="Resume Content & Output Settings", style='Title.TLabel')
        title.pack(anchor='w', padx=20, pady=5)
        
        # Folder Name Input (NEW)
        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill='x', padx=20, pady=(10, 15))
        
        folder_label = ttk.Label(folder_frame, text="Output Folder Name:", style='Field.TLabel')
        folder_label.pack(anchor='w', pady=(0, 5))
        
        # Entry for folder name
        self.folder_name_var = tk.StringVar(value="my_resume")
        folder_entry = ttk.Entry(folder_frame, 
                                textvariable=self.folder_name_var,
                                width=40)
        folder_entry.pack(fill='x', pady=5)
        
        folder_help = ttk.Label(folder_frame, 
                               text="Files will be saved to: output/[folder_name]/",
                               font=('Segoe UI', 9),
                               foreground='#666')
        folder_help.pack(anchor='w', pady=(2, 0))
        
        # ChatGPT Input Section
        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        chatgpt_label = ttk.Label(frame, 
                                 text="Paste ChatGPT Resume Output Below:",
                                 font=('Segoe UI', 11, 'bold'))
        chatgpt_label.pack(anchor='w', padx=20, pady=(5, 10))
        
        # Text area
        self.chatgpt_text_area = scrolledtext.ScrolledText(frame, 
                                                          wrap=tk.WORD,
                                                          font=('Courier New', 10),
                                                          height=15)
        self.chatgpt_text_area.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # Add sample text
        sample_text = self.get_sample_chatgpt_output()
        self.chatgpt_text_area.insert('1.0', sample_text)
        
        # File buttons frame
        file_frame = ttk.Frame(frame)
        file_frame.pack(padx=20, pady=5)
        
        ttk.Button(file_frame, text="📂 Load from File",
                  command=self.load_chatgpt_output,
                  width=15).pack(side='left', padx=2)
        
        ttk.Button(file_frame, text="💾 Save to File",
                  command=self.save_chatgpt_output,
                  width=15).pack(side='left', padx=2)

    def load_chatgpt_output(self):
        """Load ChatGPT output from file"""
        file_path = filedialog.askopenfilename(
            title="Load ChatGPT Output from File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.chatgpt_text_area.delete('1.0', tk.END)
                self.chatgpt_text_area.insert('1.0', content)
                messagebox.showinfo("Success", f"Loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_chatgpt_output(self):
        """Save ChatGPT output to file"""
        content = self.chatgpt_text_area.get('1.0', tk.END).strip()
        
        if not content:
            messagebox.showwarning("Warning", "No content to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save ChatGPT Output to File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        
    def create_generate_buttons(self):
        """Create action buttons at bottom"""
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10, side='bottom')
        
        # Right side button (primary action)
        ttk.Button(button_frame, text="🚀 Generate Resume",
                  command=self.generate_resume,
                  style='Accent.TButton').pack(side='right')
        
        # Configure accent button
        style = ttk.Style()
        style.configure('Accent.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       background='#0078D4',
                       padding=10)

    def clean_folder_name(self, folder_name):
        """
        Clean folder name by removing invalid characters
        and applying naming conventions
        """

        # --- Extract company name ---
        company_name = folder_name.split('+', 1)[0].strip()

        if company_name:
            os.makedirs("input", exist_ok=True)
            company_file_path = os.path.join("input", "company.txt")

            # Read existing companies (if file exists)
            existing_companies = set()
            if os.path.exists(company_file_path):
                with open(company_file_path, "r", encoding="utf-8") as f:
                    existing_companies = {line.strip() for line in f if line.strip()}
            
            # Check if already bid
            if company_name in existing_companies:
                messagebox.showerror("Error", "You've already bid this company. Please choose another one!")
                return None, None
        
        # Clean folder name
        # Remove invalid Windows filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        cleaned = re.sub(invalid_chars, '', folder_name)
        
        # Remove leading/trailing spaces and dots
        cleaned = cleaned.strip().strip('.')
        
        # Remove extra spaces (more than one)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Truncate if too long (Windows max path is 260 chars)
        max_length = 100  # Reasonable limit for folder names
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rstrip()
        
        # If empty after cleaning, use default
        if not cleaned:
            cleaned = "my_resume"
        
        return cleaned, company_name
    
    def write_company_to_file(self, company_name):
        """Write company name to company.txt file"""
        if not company_name:
            return
        
        os.makedirs("input", exist_ok=True)
        company_file_path = os.path.join("input", "company.txt")
        
        try:
            with open(company_file_path, "a", encoding="utf-8") as f:
                f.write(company_name + "\n")
        except Exception as e:
            print(f"Warning: Failed to write company to file: {e}")

    def collect_base_info(self):
        """Collect only base information (for save/load config)"""
        config = {
            'personal': {},
            'education': [],
            'company': []
        }
        
        # Collect personal data from fields
        for field_key, field_info in self.fields.items():
            entry = field_info['entry']
            category = field_info['category']
            value = entry.get().strip()
            
            if category == 'company':
                # Parse comma-separated company list
                if value:
                    companies = [c.strip() for c in value.split(',') if c.strip()]
                    config['company'] = companies
            elif category == 'personal':
                # Store in personal category
                if value:
                    config['personal'][field_key] = value
        
        # Collect education data from entries
        for edu_entry in self.education_entries:
            edu_data = {
                'university': edu_entry['university'].get().strip(),
                'degree': edu_entry['degree'].get().strip(),
                'edu_location': edu_entry['location'].get().strip(),
                'graduation_year': edu_entry['graduation_year'].get().strip()
            }
            # Only add if at least university is filled
            if edu_data['university']:
                config['education'].append(edu_data)
        
        return config
    
    def collect_chatgpt_output(self):
        """Collect ChatGPT output text from the UI"""
        return self.chatgpt_text_area.get('1.0', tk.END).strip()
    
    def get_sample_chatgpt_output(self):
        """Return sample ChatGPT output"""
        return """PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in backend development, specializing in microservices architecture and cloud technologies.

SKILLS
Technical: Python, Java, Spring Boot, AWS, Docker, Kubernetes, React, Node.js
Soft: Leadership, Communication, Agile Methodology

EXPERIENCE
Microsoft
Senior Software Engineer | Redmond, WA | November 2023 - Present
• Developed scalable microservices architecture
• Led team of 5 engineers
• Optimized API performance by 40%

PayPal
Software Engineer II | San Jose, CA | November 2021 - September 2023
• Built payment processing systems
• Implemented fraud detection algorithms

Tagani
Software Engineer | Makati, Philippines | October 2016 - September 2021
• Created e-commerce platform
• Developed REST APIs"""
    
    def generate_resume(self):
        """Generate the resume using collected data"""
        try:
            # Collect base info and chatgpt output separately
            config = self.collect_base_info()
            chatgpt_text = self.collect_chatgpt_output()
            
            # Validate required fields
            if not config['personal'].get('name'):
                messagebox.showerror("Error", "Please enter your Full Name")
                return
            
            if not chatgpt_text:
                messagebox.showerror("Error", "Please enter ChatGPT resume output")
                return
            
            # Clean folder name and check if company is already bid
            folder_name, company_name = self.clean_folder_name(self.folder_name_var.get().strip())
            if not folder_name:
                # Already bid or invalid - error already shown in clean_folder_name
                return

            # Add folder_name and company_name to config
            config['folder_name'] = folder_name
            config['company_name'] = company_name

            # Import and run processor
            self.run_resume_processor(config, chatgpt_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate resume: {e}")
    
    def run_resume_processor(self, config, chatgpt_text):
        """Run the resume processor"""
        try:
            # Check template folder
            template_folder = "input/template1"
            if not os.path.exists(template_folder):
                messagebox.showerror("Error", 
                    "Template folder not found.\n"
                    "Please extract your DOCX to: input/template1/")
                return
            
            # Check template document
            template_doc = "input/document.xml"
            if not os.path.exists(template_doc):
                messagebox.showerror("Error", 
                    "Template document not found.\n"
                    "Please ensure input/document.xml exists")
                return
            
            # Import processor
            from processor import ResumeProcessor
            
            # Create and run processor
            processor = ResumeProcessor(
                template_doc=template_doc,
                template_folder=template_folder,
                chatgpt_text=chatgpt_text,
                config=config
            )

            # Run processor
            result = processor.run()
            
            if result:
                pdf_result = convert_docx_to_pdf(result)
                os.startfile(pdf_result)
                company_name = config.get('company_name')
                self.on_generation_success(result, company_name)
            else:
                messagebox.showerror("Error", "Failed to generate resume")
                
        except Exception as e:
            messagebox.showerror("Error", f"Processor error: {e}")
    
    def on_generation_success(self, output_file, company_name=None):
        """Handle successful generation"""
        # Write company name to file after successful generation
        if company_name:
            self.write_company_to_file(company_name)
        
        pdf_file = output_file.replace('.docx', '.pdf')
        pdf_exists = os.path.exists(pdf_file)
        
        # Create message
        message = f"✅ Resume generated successfully!\n\n"
        message += f"📄 DOCX: {os.path.basename(output_file)}\n"
        
        if pdf_exists:
            message += f"📄 PDF:  {os.path.basename(pdf_file)}\n"
        
        message += f"\nFiles saved in: output/\n\n"
        messagebox.showinfo("Success", message)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()