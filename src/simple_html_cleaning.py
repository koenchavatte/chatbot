from langchain.docstore.document import Document
from langchain_community.document_transformers import BeautifulSoupTransformer
import os

# Adjusted file path
file_path = '../erasmus-site-parsed/opleidingen_toegepaste-informatica.html'

# Ensure the file exists before trying to open it
if not os.path.exists(file_path):
    print(f"File {file_path} does not exist.")
else:
    bs_transformer = BeautifulSoupTransformer()

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    document = [Document(page_content=html_content)]

    doc_transformed = bs_transformer.transform_documents(document, tags_to_extract=["span", "table", "li", "d", "h1", "h2", "h3", "h4", "h5", "p"], unwanted_tags=["a"])[0]
    
    # Save the cleaned content to a new file
    cleaned_file_path = '../erasmus-site-parsed/cleaned_opleidingen_toegepaste-informatica.txt'
    with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
        cleaned_file.write(doc_transformed.page_content)
    
    print(f"Cleaned content saved to {cleaned_file_path}")
