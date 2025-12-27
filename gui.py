#!/usr/bin/env python3
"""
Resume Builder GUI - Simplified Two-Tab Version
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
from pathlib import Path
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
        
        # Data storage
        self.base_data = {
            'personal': {},
            'education': {},
            'company': []
        }
        self.chatgpt_text = ""
        
        # Create UI
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#f0f0f0'
        self.root.configure(bg=bg_color)
        
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
        self.create_action_buttons()
        
    def create_base_info_tab(self, notebook):
        """Create Base Information tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text='📋 Base Information')
        
        # Create main container with scrollbar
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title = ttk.Label(scrollable_frame, text="Base Information", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Create form
        self.fields = {}
        
        # Field definitions
        field_definitions = [
            # (field_key, label_text, placeholder, row, category)
            ('name', 'Full Name:', 'John Doe', 1, 'personal'),
            ('location', 'Location:', 'San Francisco, CA', 2, 'personal'),
            ('email', 'Email:', 'john.doe@email.com', 3, 'personal'),
            ('phone', 'Phone:', '+1 (555) 123-4567', 4, 'personal'),
            ('linkedin', 'LinkedIn URL:', 'https://linkedin.com/in/johndoe', 5, 'personal'),
            
            ('university', 'University:', 'Stanford University', 7, 'education'),
            ('edu_location', 'University Location:', 'Stanford, CA', 8, 'education'),
            ('graduation_year', 'Graduation Date:', '2020', 9, 'education'),
            
            ('company', 'Companies (comma separated):', 'Microsoft, PayPal, Tagani', 11, 'company')
        ]
        
        current_row = 1
        
        for field_key, label_text, placeholder, row_num, category in field_definitions:
            # Add separator before sections
            if field_key == 'university':
                ttk.Separator(scrollable_frame, orient='horizontal').grid(
                    row=6, column=0, columnspan=2, sticky='ew', pady=10
                )
                ttk.Label(scrollable_frame, text="Education", 
                         font=('Segoe UI', 11, 'bold')).grid(
                    row=6, column=0, columnspan=2, sticky='w', pady=(10, 5)
                )
            
            if field_key == 'company':
                ttk.Separator(scrollable_frame, orient='horizontal').grid(
                    row=10, column=0, columnspan=2, sticky='ew', pady=10
                )
                ttk.Label(scrollable_frame, text="Work Experience", 
                         font=('Segoe UI', 11, 'bold')).grid(
                    row=10, column=0, columnspan=2, sticky='w', pady=(10, 5)
                )
            
            # Label
            label = ttk.Label(scrollable_frame, text=label_text, style='Field.TLabel')
            label.grid(row=row_num, column=0, sticky='w', pady=5)
            
            # Entry field
            entry = ttk.Entry(scrollable_frame, width=40)
            entry.insert(0, placeholder)
            entry.grid(row=row_num, column=1, sticky='ew', pady=5, padx=(10, 0))
            
            self.fields[field_key] = {
                'entry': entry,
                'category': category
            }
            current_row = row_num + 1
        
        # Configure grid weights
        scrollable_frame.columnconfigure(1, weight=1)
        
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
                  command=self.load_chatgpt_file,
                  width=15).pack(side='left', padx=2)
        
        ttk.Button(file_frame, text="💾 Save to File",
                  command=self.save_chatgpt_file,
                  width=15).pack(side='left', padx=2)
        
    def create_action_buttons(self):
        """Create action buttons at bottom"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        # Left side buttons
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side='left')
        
        ttk.Button(left_frame, text="⚙️ Load Config",
                  command=self.load_config).pack(side='left', padx=2)
        
        ttk.Button(left_frame, text="💾 Save Config",
                  command=self.save_config).pack(side='left', padx=2)
        
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
    
    def load_chatgpt_file(self):
        """Load ChatGPT output from file"""
        file_path = filedialog.askopenfilename(
            title="Load ChatGPT Output",
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
    
    def save_chatgpt_file(self):
        """Save ChatGPT output to file"""
        content = self.chatgpt_text_area.get('1.0', tk.END).strip()
        
        if not content:
            messagebox.showwarning("Warning", "No content to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save ChatGPT Output",
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
    
    def load_config(self):
        """Load configuration from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Load data into fields
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
                    else:
                        # Handle personal and education fields
                        if category in config and field_key in config[category]:
                            entry.delete(0, tk.END)
                            entry.insert(0, config[category][field_key])
                
                # Load ChatGPT text
                if 'chatgpt_text' in config:
                    self.chatgpt_text_area.delete('1.0', tk.END)
                    self.chatgpt_text_area.insert('1.0', config['chatgpt_text'])
                
                messagebox.showinfo("Success", f"Loaded configuration")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
    
    def save_config(self):
        """Save configuration to JSON file"""
        config = self.collect_data()
        
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Configuration saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")
    

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

            # Check duplication
            if company_name in existing_companies:
                messagebox.showerror("Error", "You've already bid this company. Please choose another one.!")
                return ""
            else:
                with open(company_file_path, "a", encoding="utf-8") as f:
                    f.write(company_name + "\n")


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
        
        return cleaned

    def collect_data(self):
        """Collect all data from the UI"""
        # Initialize data structure
        config = {
            'personal': {},
            'education': {},
            'company': [],
            'chatgpt_text': '',
            'folder_name': self.clean_folder_name(self.folder_name_var.get().strip())
        }
        
        # Collect data from fields
        for field_key, field_info in self.fields.items():
            entry = field_info['entry']
            category = field_info['category']
            value = entry.get().strip()
            
            if category == 'company':
                # Parse comma-separated company list
                if value:
                    companies = [c.strip() for c in value.split(',') if c.strip()]
                    config['company'] = companies
            else:
                # Store in appropriate category
                if value:
                    config[category][field_key] = value
        
        # Collect ChatGPT text
        config['chatgpt_text'] = self.chatgpt_text_area.get('1.0', tk.END).strip()
        
        return config
    
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
            # Collect data
            config = self.collect_data()
            
            # Validate required fields
            if not config['personal'].get('name'):
                messagebox.showerror("Error", "Please enter your Full Name")
                return
            
            if not config['chatgpt_text']:
                messagebox.showerror("Error", "Please enter ChatGPT resume output")
                return
            
            # Save files
            self.save_input_files(config)
            
            # Validate folder name
            folder_name = config['folder_name']
            if not folder_name or folder_name.strip() == "":
                messagebox.showerror("Error", "Please enter a folder name")
                return

            # Import and run processor
            self.run_resume_processor(config)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate resume: {e}")
    
    def save_input_files(self, config):
        """Save input files for processing"""
        # Create input directory
        os.makedirs('input', exist_ok=True)
        
        # Prepare base_data
        base_data = {
            'personal': config['personal'],
            'company': config['company'],
            'education': config['education']
        }
        
        # Save base_data.json
        with open('input/base_data.json', 'w', encoding='utf-8') as f:
            json.dump(base_data, f, indent=2, ensure_ascii=False)
        
        # Save chatgpt.txt
        with open('input/chatgpt.txt', 'w', encoding='utf-8') as f:
            f.write(config['chatgpt_text'])
        
        print("✅ Saved input files")
    
    def run_resume_processor(self, config):
        """Run the resume processor"""
        try:
            # Check template folder
            template_folder = "input/template1"
            if not os.path.exists(template_folder):
                messagebox.showerror("Error", 
                    "Template folder not found.\n"
                    "Please extract your DOCX to: input/template1/")
                return
            
            # Import processor
            try:
                from processor import ResumeProcessor
            except ImportError:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from processor import ResumeProcessor
            
            # Create and run processor
            processor = ResumeProcessor(
                template_doc="input/document.xml",
                template_folder=template_folder,
                chatgpt_file="input/chatgpt.txt",
                config=config
            )

            print(config)
            
            # Run processor
            result = processor.run()
            
            if result:
                pdf_result = convert_docx_to_pdf(result)
                os.startfile(pdf_result)
                self.on_generation_success(result)
            else:
                messagebox.showerror("Error", "Failed to generate resume")
                
        except Exception as e:
            messagebox.showerror("Error", f"Processor error: {e}")
    
    def on_generation_success(self, output_file):
        """Handle successful generation"""
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

def main():
    """Main entry point"""
    app = ResumeBuilderGUI()
    app.run()

if __name__ == "__main__":
    main()