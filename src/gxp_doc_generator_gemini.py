import os
import json
from pathlib import Path
from dotenv import load_dotenv
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_COLOR_INDEX
import re
from datetime import datetime
import google.generativeai as genai

class GxPDocumentGenerator:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Configure Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Initialize paths
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data'
        self.output_path = self.base_path / 'output'
        self.prompt_path = self.base_path / 'prompt'
        self.output_path.mkdir(exist_ok=True)
        self.default_font_name = "Arial"

    def load_system_prompt(self):
        """Load the system prompt template"""
        with open(self.prompt_path / 'system.txt', 'r') as f:
            return f.read()

    def load_user_stories(self):
        """Load all user stories from the data/userstories directory"""
        stories = []
        stories_path = self.data_path / 'userstories'
        for story_file in stories_path.glob('BLOOD-*.txt'):
            with open(story_file, 'r') as f:
                stories.append(f.read())
        return stories

    def load_database_design(self):
        """Load database design from the data/database-design directory"""
        with open(self.data_path / 'database-design' / 'blood_collection_schema.sql', 'r') as f:
            return f.read()

    def generate_gxp_content(self, system_prompt, user_stories, db_design):
        """Generate GxP documentation content using Gemini API"""
        try:
            # Prepare the prompt
            prompt = f"""
            Based on the following inputs, generate a GxP Function Detail Design Document. Structure the content with clear headings and subheadings, following a hierarchical numbering system (e.g., 1., 1.1, 1.1.1, etc.). Ensure each section is properly delineated and the content is well-organized.
            
            User Stories:
            {'-' * 80}
            {chr(10).join(user_stories)}
            {'-' * 80}

            Database Design:
            {'-' * 80}
            {db_design}
            {'-' * 80}
            
            {system_prompt}
            """

            # Initialize chat with system prompt
            chat = self.model.start_chat(history=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "I understand. I will help create a GxP Function Detail Design Document following the specified format with PLAIN TEXT ONLY."}]
                }
            ])

            # Generate content using chat
            response = chat.send_message(prompt)

            # Return the generated content
            return response.text

        except Exception as e:
            print(f"Error generating content: {str(e)}")
            raise

    def preprocess_content(self, content):
        """Remove markup symbols and formatting characters"""
        # Remove code blocks
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        # Remove table-like structures
        content = re.sub(r"\|.*\|", "", content)
        # Remove any other markup symbols
        content = re.sub(r"[*+-]+", "", content)
        # Remove extra spaces and newlines
        content = re.sub(r"\s+", " ", content).strip()

        return content

    def parse_sections(self, content):
        """Parse content into sections with proper hierarchy and indentation"""
        sections = []
        lines = content.split('\n')
        current_section = None
        section_stack = []  # Keep track of parent sections
        
        for line in lines:
            line = line.rstrip()  # Remove trailing whitespace but keep indentation
            if not line:
                continue
                
            # Check if line is a heading (starts with numbers)
            heading_match = re.match(r'^(\d+(\.\d+)*)\.\s+(.+)$', line)
            if heading_match:
                # Calculate heading level based on number of dots
                heading_number = heading_match.group(1)
                dots_count = heading_number.count('.')
                level = dots_count + 1
                
                # Create section object
                current_section = {
                    'type': 'heading',
                    'level': level,
                    'text': line.strip(),
                    'number': heading_number,
                    'dots_count': dots_count
                }
                
                # Update section stack
                while section_stack and section_stack[-1]['level'] >= level:
                    section_stack.pop()
                if section_stack:
                    current_section['parent_section'] = section_stack[-1]
                section_stack.append(current_section)
                sections.append(current_section)
            else:
                # For content lines
                if current_section:
                    content_section = {
                        'type': 'content',
                        'level': current_section['level'],
                        'text': line.strip(),
                        'parent_section': current_section,
                        'dots_count': current_section['dots_count']
                    }
                    sections.append(content_section)
        
        return sections

    def create_word_document(self, content):
        """Create a Word document with the generated content"""
        doc = Document()
        
        # Define styles first
        self.define_styles(doc)
        
        # Add title page
        title = doc.add_paragraph('GxP Function Detail Design Document', style='Title')
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add timestamp on title page
        timestamp = doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', style='Timestamp')
        timestamp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add page break after title page
        doc.add_page_break()
        
        # Add table of contents placeholder
        doc.add_paragraph('Table of Contents', style='TOC Heading')
        doc.add_paragraph('', style='Normal')  # Placeholder for TOC
        doc.add_page_break()
        
        # Process content
        sections = self.parse_sections(content)
        
        # Add sections to document
        for section in sections:
            # Calculate indentation (40 points = approximately 4 spaces)
            indent_points = Pt(section['indent_level'] * 40)
            
            if section['type'] == 'heading':
                # For headings, use the built-in heading style
                heading = doc.add_heading(section['text'], level=section['level'])
                heading.paragraph_format.left_indent = indent_points
                heading.paragraph_format.space_after = Pt(12)
            else:
                # For content, use normal style with proper indentation
                para = doc.add_paragraph(section['text'], style='Normal')
                para.paragraph_format.left_indent = indent_points
                para.paragraph_format.space_after = Pt(6)
                para.paragraph_format.space_before = Pt(6)
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_path / f'GxP_Documentation_{timestamp}.docx'
        doc.save(output_file)
        return output_file

    def create_txt_document(self, content):
        """Create a TXT document with the generated content"""
        # Process content
        sections = self.parse_sections(content)
        print(sections)
        
        # Create the output text
        output_lines = []
        
        # Add title and timestamp
        output_lines.append('GxP Function Detail Design Document')
        output_lines.append('')
        output_lines.append(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        output_lines.append('')
        output_lines.append('Table of Contents')
        output_lines.append('')
        
        last_section = None
        
        # Add sections with proper indentation
        for section in sections:
            # Calculate base indentation based on dots in section number
            if section['type'] == 'heading':
                # Add blank line between sections of same or lower level
                if last_section and last_section['type'] == 'heading':
                    if section['level'] <= last_section['level']:
                        output_lines.append('')
                
                # Calculate indentation for headings
                if section['dots_count'] == 0:  # Top level (1., 2., etc)
                    indent = ''
                else:
                    # Each dot means one more level of indentation
                    indent = '    ' * section['dots_count']
                
                output_lines.append(f"{indent}{section['text']}")
                
            else:  # Content
                # Content is always indented one more level than its parent heading
                if section['parent_section']:
                    parent_dots = section['parent_section']['dots_count']
                    
                    # Special handling for Validation/Processing sections
                    if 'Validation/Processing' in section['parent_section']['text']:
                        indent = '    ' * (parent_dots + 2)
                    else:
                        indent = '    ' * (parent_dots + 1)
                else:
                    indent = '    '  # Default indentation for content
                
                output_lines.append(f"{indent}{section['text']}")
            
            last_section = section
        
        # Join lines with newlines
        output_text = '\n'.join(output_lines)
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_path / f'GxP_Documentation_{timestamp}.txt'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        return output_file

    def define_styles(self, doc):
        """Define document styles"""
        styles = doc.styles

        # Title Style
        try:
            title_style = styles['CustomTitle']
        except KeyError:
            title_style = styles.add_style('CustomTitle', WD_STYLE_TYPE.PARAGRAPH)
        title_style.base_style = styles['Normal']
        title_font = title_style.font
        title_font.name = 'Arial'
        title_font.size = Pt(24)
        title_font.bold = True
        title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_style.paragraph_format.space_after = Pt(30)

        # TOC Heading Style
        try:
            toc_style = styles['TOC Heading']
        except KeyError:
            toc_style = styles.add_style('TOC Heading', WD_STYLE_TYPE.PARAGRAPH)
        toc_style.font.name = 'Arial'
        toc_style.font.size = Pt(16)
        toc_style.font.bold = True
        toc_style.paragraph_format.space_after = Pt(24)

        # Timestamp Style
        try:
            timestamp_style = styles['Timestamp']
        except KeyError:
            timestamp_style = styles.add_style('Timestamp', WD_STYLE_TYPE.PARAGRAPH)
        timestamp_style.base_style = styles['Normal']
        timestamp_font = timestamp_style.font
        timestamp_font.name = 'Arial'
        timestamp_font.size = Pt(10)
        timestamp_font.italic = True
        timestamp_style.paragraph_format.space_after = Pt(30)

        # Normal Style
        normal_style = styles['Normal']
        normal_font = normal_style.font
        normal_font.name = 'Arial'
        normal_font.size = Pt(11)
        normal_style.paragraph_format.space_after = Pt(6)
        normal_style.paragraph_format.line_spacing = 1.15

        # Heading Styles
        for i in range(1, 10):
            heading_style = styles.add_style(f'Custom Heading {i}', WD_STYLE_TYPE.PARAGRAPH)
            heading_style.font.name = 'Arial'
            heading_style.font.bold = True
            # Decrease size for each heading level
            heading_style.font.size = Pt(16 - (i-1) * 2)
            heading_style.paragraph_format.space_before = Pt(12)
            heading_style.paragraph_format.space_after = Pt(6)
            if i == 1:
                heading_style.paragraph_format.keep_with_next = True
                heading_style.paragraph_format.page_break_before = True

    def generate(self):
        """Main method to orchestrate the document generation process"""
        try:
            print("Loading input files...")
            system_prompt = self.load_system_prompt()
            user_stories = self.load_user_stories()
            db_design = self.load_database_design()

            print("Generating GxP documentation content...")
            content = self.generate_gxp_content(system_prompt, user_stories, db_design)

            # print("Creating Word document...")
            # docx_file = self.create_word_document(content)
            # print(f"Word document generated successfully: {docx_file}")

            print("Creating TXT document...")
            txt_file = self.create_txt_document(content)
            print(f"TXT document generated successfully: {txt_file}")

            # return docx_file, txt_file
            return txt_file
        except Exception as e:
            print(f"Error in document generation process: {str(e)}")
            raise