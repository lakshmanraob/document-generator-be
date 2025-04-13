# src/gxp_doc_generator_gemini.py
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
    def __init__(self, user_stories_path=None, db_schema_path=None): # Accept paths
        # Load environment variables
        load_dotenv()

        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)

        # Consider making the model configurable or handling potential errors
        try:
            # Use a known, stable model. Ensure it's available.
            # Check Gemini documentation for current model names.
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            # Handle error appropriately, maybe raise it or set self.model to None
            raise ValueError(f"Could not initialize Gemini model: {e}")

        # Base path is the directory containing the 'src' directory (project root)
        self.base_path = Path(__file__).parent.parent
        # Output path relative to the project root
        self.output_path = self.base_path / 'output'
        # Prompt path relative to the project root
        self.prompt_path = self.base_path / 'prompt'
        self.output_path.mkdir(parents=True, exist_ok=True) # Ensure parent dirs exist
        self.prompt_path.mkdir(parents=True, exist_ok=True) # Ensure prompt dir exists
        self.default_font_name = "Arial"

        # Store provided input file paths as Path objects
        self.user_stories_path = Path(user_stories_path) if user_stories_path else None
        self.db_schema_path = Path(db_schema_path) if db_schema_path else None

    def load_system_prompt(self):
        """Load the system prompt template"""
        # Construct path relative to base path
        prompt_file = self.prompt_path / 'system.txt'
        if not prompt_file.exists():
             # Attempt alternative path if structure differs slightly
             prompt_file = Path(__file__).parent / 'prompt' / 'system.txt'
             if not prompt_file.exists():
                raise FileNotFoundError(f"Error: System prompt file not found at expected locations relative to project root or script location.")

        try:
            print(prompt_file)
            with open(prompt_file, 'r', encoding='utf-8') as f: # Specify encoding
                return f.read()
        except Exception as e:
            print(f"Error reading system prompt file {prompt_file}: {e}")
            raise # Re-raise the exception after logging


    def load_user_stories(self):
        """Load user stories content from the provided file path."""
        if not self.user_stories_path:
             raise ValueError("User stories file path was not provided to the generator.")
        if not self.user_stories_path.exists():
            raise FileNotFoundError(f"User stories file not found at the provided path: {self.user_stories_path}")
        try:
            with open(self.user_stories_path, 'r', encoding='utf-8') as f: # Specify encoding
                 # Return as a list containing one item (the whole file content)
                 # to match the expected format in generate_gxp_content
                return [f.read()]
        except Exception as e:
            print(f"Error reading user stories file {self.user_stories_path}: {e}")
            raise


    def load_database_design(self):
        """Load database design content from the provided file path."""
        if not self.db_schema_path:
            raise ValueError("Database schema file path was not provided to the generator.")
        if not self.db_schema_path.exists():
            raise FileNotFoundError(f"Database schema file not found at the provided path: {self.db_schema_path}")
        try:
            with open(self.db_schema_path, 'r', encoding='utf-8') as f: # Specify encoding
                return f.read()
        except Exception as e:
            print(f"Error reading database schema file {self.db_schema_path}: {e}")
            raise

    def generate_gxp_content(self, system_prompt, user_stories, db_design):
        """Generate GxP documentation content using Gemini API"""
        if not self.model:
             raise RuntimeError("Gemini model was not initialized successfully.")
        try:
            # Ensure user_stories is joined correctly if it's a list
            user_stories_text = "\n".join(user_stories) # Use newline as separator

            # Ensure inputs are not excessively large - add checks if needed
            # Example check (adjust limits as needed):
            # MAX_INPUT_LENGTH = 100000 # Example character limit
            # if len(user_stories_text) > MAX_INPUT_LENGTH or len(db_design) > MAX_INPUT_LENGTH:
            #     raise ValueError("Input data exceeds maximum allowed length.")

            prompt = f"""
            Based on the following inputs, generate a GxP Function Detail Design Document. Structure the content with clear headings and subheadings, following a hierarchical numbering system (e.g., 1., 1.1, 1.1.1, etc.). Ensure each section is properly delineated and the content is well-organized. Output should be PLAIN TEXT suitable for a .txt file, using indentation for structure.

            User Stories:
            {'-' * 80}
            {user_stories_text}
            {'-' * 80}

            Database Design:
            {'-' * 80}
            {db_design}
            {'-' * 80}

            System Requirements/Instructions:
            {'-' * 80}
            {system_prompt}
            {'-' * 80}
            """

            # Initialize chat with system prompt (optional, depends on model preference)
            # Some models work better with direct generation requests
            # chat = self.model.start_chat(history=[
            #     {
            #         "role": "user",
            #         "parts": [{"text": system_prompt}]
            #     },
            #     {
            #         "role": "model",
            #         "parts": [{"text": "I understand. I will help create a GxP Function Detail Design Document following the specified format with PLAIN TEXT ONLY."}]
            #     }
            # ])
            # response = chat.send_message(prompt)

            # Direct generation request
            response = self.model.generate_content(prompt)


            # Check for safety ratings or blocks if applicable
            # (Refer to Google AI documentation for handling safety attributes)
            # if response.prompt_feedback.block_reason:
            #     raise ValueError(f"Content generation blocked due to: {response.prompt_feedback.block_reason}")

            # Return the generated text
            return response.text

        except Exception as e:
            print(f"Error generating content via Gemini API: {str(e)}")
            # Consider logging traceback here for complex errors
            raise


    def parse_sections(self, content):
        """Parse content into sections with proper hierarchy and indentation for TXT output"""
        sections = []
        lines = content.split('\n')
        current_section_info = {'level': 0, 'indent_level': -1} # Track current nesting
        section_stack = [{'level': 0, 'indent_level': -1}] # Stack to manage hierarchy

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line: # Skip empty lines
                continue

            # Try to match heading format (e.g., "1. Heading", "1.2. Subheading")
            heading_match = re.match(r'^\s*(\d+(\.\d+)*)\.?\s+(.+)$', line)

            if heading_match:
                heading_number = heading_match.group(1)
                level = heading_number.count('.') + 1
                heading_text = heading_match.group(3).strip()
                # Use heading level to determine base indent
                indent_level = level - 1

                current_section_info = {
                    'type': 'heading',
                    'level': level,
                     # Reconstruct text for consistency
                    'text': f"{heading_number}. {heading_text}",
                    'number': heading_number,
                    'indent_level': indent_level
                }
                sections.append(current_section_info)

                # Manage stack for potential future child content indentation
                while section_stack[-1]['level'] >= level:
                    section_stack.pop()
                section_stack.append(current_section_info)

            else:
                # Treat as content line if not a heading
                # Indent based on the last known heading's level
                parent_section = section_stack[-1]
                # Content is indented one level deeper than its parent heading
                indent_level = parent_section['indent_level'] + 1

                content_section = {
                    'type': 'content',
                    'level': parent_section['level'], # Associated with parent heading level
                    'text': stripped_line, # Store the stripped content line
                    'indent_level': indent_level
                }
                sections.append(content_section)

        return sections

    def create_word_document(self, content):
        """Placeholder/Optional: Create a Word document with the generated content"""
        print("Word document creation is currently optional/not fully implemented.")
        # If needed, implement using the parse_sections logic adapted for Word styles/indentation
        # Ensure self.define_styles(doc) is called and works correctly.
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_path / f'GxP_Documentation_{timestamp_str}.docx'
        print(f"Placeholder for Word document at: {output_file}")
        # Example:
        # doc = Document()
        # self.define_styles(doc)
        # ... (add title, TOC placeholder, sections using parse_sections and doc.add_paragraph/heading) ...
        # doc.save(output_file)
        return None # Return None or the path if implemented


    def create_txt_document(self, content):
        """Create a TXT document with the generated content, using parsed sections"""
        # Process content using the parser optimized for TXT structure
        sections = self.parse_sections(content)

        output_lines = []

        # Add title and timestamp
        output_lines.append('GxP Function Detail Design Document')
        output_lines.append('')
        output_lines.append(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        output_lines.append('')
        # output_lines.append('Table of Contents') # Optional TOC placeholder
        # output_lines.append('')

        last_section_level = 0
        # Add sections with proper indentation
        for i, section in enumerate(sections):
             # Add blank line between different top-level sections (level 1)
             # or before a heading that's not immediately following another heading
            if section['type'] == 'heading':
                 # Add space before a new top-level heading if not the first heading
                 if section['level'] == 1 and i > 0 and sections[i-1]['level'] > 0:
                     output_lines.append('')
                 # Add space before a heading if the previous line was content
                 elif i > 0 and sections[i-1]['type'] == 'content':
                      output_lines.append('')
                 last_section_level = section['level'] # Track last heading level

            # Calculate indentation based on indent_level from parse_sections
            # Use 4 spaces per indent level
            indent = '    ' * section['indent_level']

            output_lines.append(f"{indent}{section['text']}")

        # Join lines with newlines
        output_text = '\n'.join(output_lines)

        # Save the document
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure output path is used correctly relative to project root
        output_file = self.output_path / f'GxP_Documentation_{timestamp_str}.txt'

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"TXT document saved successfully to: {output_file}")
        except Exception as e:
            print(f"Error writing TXT file {output_file}: {e}")
            raise

        return output_file # Return the Path object

    def define_styles(self, doc):
        """Define document styles (Only relevant for create_word_document)"""
        styles = doc.styles
        # Use default font name stored in self
        default_font = self.default_font_name

        # --- Define Custom Styles ---
        # Style for the main title
        try:
            style = styles['CustomTitle']
        except KeyError:
            style = styles.add_style('CustomTitle', WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = styles['Normal']
        font = style.font
        font.name = default_font
        font.size = Pt(24)
        font.bold = True
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        style.paragraph_format.space_after = Pt(18)

        # Style for the Table of Contents heading
        try:
            style = styles['TOC Heading']
        except KeyError:
            style = styles.add_style('TOC Heading', WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = styles['Heading 1'] # Base on Heading 1 for outline level
        font = style.font
        font.name = default_font
        font.size = Pt(16)
        font.bold = True
        style.paragraph_format.space_after = Pt(12)
        style.paragraph_format.keep_with_next = True

        # Style for the timestamp
        try:
            style = styles['Timestamp']
        except KeyError:
            style = styles.add_style('Timestamp', WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = styles['Normal']
        font = style.font
        font.name = default_font
        font.size = Pt(10)
        font.italic = True
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        style.paragraph_format.space_after = Pt(30)

        # --- Customize Base Styles ---
        # Normal Style
        style = styles['Normal']
        font = style.font
        font.name = default_font
        font.size = Pt(11)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.line_spacing = 1.15

        # Ensure built-in heading styles use the default font
        for i in range(1, 10):
            try:
                style = styles[f'Heading {i}']
                style.font.name = default_font
                # Optional: Adjust heading sizes, spacing, etc.
                # style.font.size = Pt(16 - i)
                # style.paragraph_format.space_before = Pt(12)
                # style.paragraph_format.space_after = Pt(6)
            except KeyError:
                continue # Ignore if style doesn't exist


    def generate(self):
        """Main method to orchestrate the document generation process"""
        output_file_path = None # Initialize
        try:
            print("Initiating document generation...")
            # 1. Load system prompt first
            print("Loading system prompt...")
            system_prompt = self.load_system_prompt()
            print("System prompt loaded.")

             # 2. Load user stories and db design using the paths provided in __init__
            print("Loading user stories...")
            user_stories = self.load_user_stories() # Reads from self.user_stories_path
            print("User stories loaded.")

            print("Loading database design...")
            db_design = self.load_database_design() # Reads from self.db_schema_path
            print("Database design loaded.")

            # 3. Generate content via API
            print("Generating GxP documentation content via API...")
            content = self.generate_gxp_content(system_prompt, user_stories, db_design)
            print("Content generation complete.")
            if not content or not content.strip():
                 raise ValueError("Generated content is empty.")

            # 4. Decide which output format(s) you need and create them
            # print("Creating Word document...")
            # docx_file = self.create_word_document(content) # Optional
            # if docx_file: print(f"Word document generated: {docx_file}")

            print("Creating TXT document...")
            txt_file_path = self.create_txt_document(content) # Generate TXT
            if not txt_file_path:
                 raise RuntimeError("Failed to create TXT document.")
            print(f"TXT document generation successful: {txt_file_path}")
            output_file_path = txt_file_path # Set the path to return

            # Return the path of the generated file the API needs to serve
            # Ensure it returns a Path object or string as expected by the endpoint
            return output_file_path

        except FileNotFoundError as e:
             # Handle missing input files gracefully
             print(f"Error: Input file not found during generation - {e}")
             # Re-raise specific error or a general one for the API
             raise FileNotFoundError(f"Generation failed: Required input file missing. {e}")
        except ValueError as e:
             # Handle other value errors (e.g., empty content, API key missing)
             print(f"Error during generation: {e}")
             raise ValueError(f"Generation failed: {e}")
        except Exception as e:
             # Catch-all for other unexpected errors
            print(f"Unexpected error in document generation process: {str(e)}")
            import traceback
            traceback.print_exc() # Log detailed error
            raise RuntimeError(f"An unexpected error occurred during document generation: {str(e)}")
