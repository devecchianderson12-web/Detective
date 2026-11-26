

def to_upper(text):
    return text.upper()


def to_lower(text):
    return text.lower()


def format_number(number):
    text = str(number)
    decimal_separator = text.find(',')
    if decimal_separator == -1:
        decimal_separator = text.find('.')
    if decimal_separator == -1:
        text_len = len(text)
    else:
        text_len = decimal_separator
    k = 3
    while k < text_len:
        i = text_len - k
        if i == 0 and text[0] == '-':
            break
        text = text[0:i] + '.' + text[i:]
        text_len += 1
        k += 4

    return text


