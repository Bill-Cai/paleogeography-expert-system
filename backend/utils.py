import aiofiles
import urllib
import uuid
from md2pdf.core import md2pdf

async def write_to_file(filename: str, text: str) -> None:
    """Asynchronously write text to a file in UTF-8 encoding.

    Args:
        filename (str): The filename to write to.
        text (str): The text to write.
    """
    # Convert text to UTF-8, replacing any problematic characters
    text_utf8 = text.encode('utf-8', errors='replace').decode('utf-8')

    async with aiofiles.open(filename, "w", encoding='utf-8') as file:
        await file.write(text_utf8)

async def write_md_to_pdf(text: str) -> str:
    """Converts Markdown text to a PDF file and returns the file path.

    Args:
        text (str): Markdown text to convert.

    Returns:
        str: The encoded file path of the generated PDF.
    """
    task = uuid.uuid4().hex
    file_path = f"outputs/{task}"
    await write_to_file(f"{file_path}.md", text)

    try:
        md2pdf(f"{file_path}.pdf",
               md_content=None,
               md_file_path=f"{file_path}.md",
               css_file_path=None,
               base_url=None)
        print(f"Report written to {file_path}.pdf")
    except Exception as e:
        print(f"Error in converting Markdown to PDF: {e}")
        return ""

    encoded_file_path = urllib.parse.quote(f"{file_path}.pdf")
    return encoded_file_path
