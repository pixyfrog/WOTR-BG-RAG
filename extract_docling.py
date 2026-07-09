from docling.document_converter import DocumentConverter

def run_docling_extractor():
    print("🐘 Initializing Docling layout analysis engine...")
    converter = DocumentConverter()
    
    print("⏳ Processing 'full_rules.pdf' using visual layout intelligence...")
    print("   (This will take a minute because it builds a smart map of columns and tables!)")
    
    # Run the visual conversion
    result = converter.convert("full_rules.pdf")
    
    # Export it directly to clean markdown text
    markdown_text = result.document.export_to_markdown()
    
    with open("wotr_docling_rules.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)
        
    print("\n🎉 Done! Visual outline extracted cleanly to 'wotr_docling_rules.md'")

if __name__ == "__main__":
    run_docling_extractor()