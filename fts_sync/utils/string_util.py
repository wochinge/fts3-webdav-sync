
def remove_quotes(text):
    if (text.startswith('"') or text.startswith("'")) and (text.endswith('"') or text.endswith("'")):
        return text[1 : -1]
    return text
