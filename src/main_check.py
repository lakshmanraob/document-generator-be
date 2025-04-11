# from gxp_doc_generator import GxPDocumentGenerator
from gxp_doc_generator_gemini import GxPDocumentGenerator

def main():
    try:
        generator = GxPDocumentGenerator()
        output_file = generator.generate()
        print(f"GxP documentation generated successfully at: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()