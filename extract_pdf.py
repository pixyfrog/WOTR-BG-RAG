import os
from markitdown import MarkItDown

def convert_pdf_to_markdown():
    pdf_filename = "full_rules.pdf"
    output_filename = "wotr_full_rules.md"
    
    # Check if the PDF actually exists in the folder
    if not os.path.exists(pdf_filename):
        print(f"❌ Error: Could not find '{pdf_filename}' in this folder.")
        print("Please copy your rulebook PDF here and rename it to 'full_rules.pdf'.")
        return

    print(f"📄 Found '{pdf_filename}'. Starting Markdown extraction...")
    print("⏳ This might take a minute depending on how large the rulebook is...")
    
    try:
        # Initialize Microsoft's extraction engine
        md_extractor = MarkItDown()
        
        # Convert the document
        result = md_extractor.convert(pdf_filename)
        
        # Save the extracted markdown text to a file
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        print(f"\n🎉 Success! Clean outline saved to: '{output_filename}'")
        print("Go open that file and check out how clean the headings and tables look!")
        
    except Exception as e:
        print(f"❌ An error occurred during conversion: {e}")

if __name__ == "__main__":
    convert_pdf_to_markdown()