import unicodedata

def is_tamil_text(text):
    """
    Detect if input contains Tamil characters
    Tamil Unicode block: 0B80–0BFF
    """
    tamil_range = range(0x0B80, 0x0BFF)
    return any(ord(char) in tamil_range for char in text)
