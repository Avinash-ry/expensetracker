import PyPDF2


def parse_pdf(file_path, num_lines_to_skip):
    """Parse a PDF file and print each line line by line, skipping the specified number of lines."""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            line_count = 0  # To count the lines and manage skipping

            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        if line_count >= num_lines_to_skip:
                            print(line)
                        line_count += 1
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
file_path = 'CreditCardStatement (2).pdf'  # Replace 'yourfile.pdf' with the path to your PDF file
num_lines_to_skip = int(input("Enter the number of lines to skip: "))  # Get user input for the number of lines to skip
parse_pdf(file_path, num_lines_to_skip)
