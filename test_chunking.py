from pypdf import PdfReader


reader = PdfReader("test.pdf")

full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"


def split_text_into_chunks(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    text_length = len(text)
    

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

chunks = split_text_into_chunks(full_text)
print(chunks[:3])  # Print the first 3 chunks for verification