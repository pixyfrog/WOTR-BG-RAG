import re

def clean_extracted_text():
    input_filename = "wotr_full_rules.md"
    output_filename = "wotr_fully_cleaned.md"
    
    print(f"🧹 Reading raw data from '{input_filename}'...")
    
    with open(input_filename, "r", encoding="utf-8") as f:
        text = f.read()

    # --- 1. Strip Out Page Running Headers ---
    # Matches patterns like "2 • War of the Ring — Second Edition Chapter I: Introduction • 3"
    print("✂️ Removing page numbers and running headers...")
    header_pattern = r"\d+\s*•\s*War of the Ring\s*—\s*Second Edition.*?\s*•\s*\d+"
    text = re.sub(header_pattern, "", text)
    
    # Also catch simple "Page Number • Game Name" variants
    text = re.sub(r"\d+\s*•\s*War of the Ring\s*—\s*Second Edition", "", text)

    # --- 2. Fix the Doubled Heading Glitch ("CCHHAAPPTTEERR II::") ---
    print("🩹 Fixing doubled font-shadow characters...")
    def fix_doubled_words(match):
        word = match.group(0)
        # Take every second character to reconstruct the single word
        cleaned_word = word[::2]
        return f"\n\n## {cleaned_word} "

    # Finds words where every character is immediately repeated (e.g., CCHHAAPPTTEERR)
    text = re.sub(r"\b([A-Z])\1([A-Z])\2([A-Z])\3([A-Z])\4([A-Z])\5([A-Z])\6([A-Z])\7([A-Z])\8([A-Z])\9.*?\b", fix_doubled_words, text)

    # --- 3. Fix the Spaced-Out Heading Glitch ("II NN TT RR OO DD UU CC TT II OO NN") ---
    print("🏷️ Formatting spaced headings and converting to Markdown titles...")
    def fix_spaced_headers(match):
        spaced_text = match.group(0)
        # Strip out all extra spaces to join the word back together
        joined_word = "".join(spaced_text.split())
        return f"\n\n# {joined_word}\n"

    # Finds sequences of single capitalized letters separated by spaces (minimum 4 letters long)
    text = re.sub(r"\b[A-Z]\s+[A-Z]\s+[A-Z]\s+[A-Z](?:\s+[A-Z])*\b", fix_spaced_headers, text)

    # --- 4. Clean Up Multi-Blank Lines ---
    print("✨ Squeezing out excessive blank space lines...")
    text = re.sub(r"\n{3,}", "\n\n", text)

    # --- 5. Save the Cleaned File ---
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(text.strip())
        
    print(f"\n🎉 Success! Beautifully structured rules file saved to: '{output_filename}'")
    print("Take a look at it now—the headers should be readable and properly formatted!")

if __name__ == "__main__":
    clean_extracted_text()