from framework.assets import *

def generate_olpc_dic(source_file, min_word_size, max_word_size):
    lines = load_data(source_file, ';', True, False)
    words = {}
    for line in lines:
        line_text = ('').join(line[1:len(line)])
        start = line_text.find('(')
        end_of_remove = False
        while not end_of_remove:
            start = line_text.find('(')
            if start == -1:
                end_of_remove = True
            else:
                end = line_text.find(')', start)
                if end == -1:
                    end_of_remove = True
                else:
                    line_text = line_text[0:start - 1] + line_text[end + 1:]

        line_words = line_text.split()
        for word in line_words:
            word = word.strip().lower()
            while word.endswith(',') or word.endswith('"') or word.endswith('!') or word.endswith('.') or word.endswith('-'):
                word = word[:len(word) - 1]

            while word.startswith('!') or word.startswith('(') or word.startswith('"') or word.startswith('¡'):
                word = word[1:len(word)]

            if word != '' and word != '!' and word != '|' and not word[0].isdigit():
                index = word.find('/')
                if index == -1:
                    index = word.find(',')
                if index == -1:
                    index = word.find('-')
                    if index == -1:
                        index = word.find("'")
                        if index == -1:
                            if word not in words:
                                words[word] = word
                    else:
                        word1 = word[:index]
                        word2 = word[index + 1:]
                        if word1 not in words:
                            words[word1] = word1
                        if word2 not in words:
                            words[word2] = word2
                else:
                    prefix = word[:index]
                    suffix = word[index + 1:]
                    if len(suffix) >= len(prefix):
                        word1 = prefix
                        word2 = suffix
                    elif suffix == 's':
                        word1 = prefix
                        word2 = prefix + suffix
                    else:
                        word1 = prefix
                        word2 = prefix[:len(prefix) - len(suffix)] + suffix
                    if word1 not in words:
                        words[word1] = word1
                    if word2 not in words:
                        words[word2] = word2

    new_words = {}
    for word in words:
        if len(word) >= min_word_size and len(word) <= max_word_size:
            word = remove_accents(word)
            if word not in new_words:
                new_words[word] = word

    words = new_words
    word_list = []
    for word in words:
        word_list.append(word)

    word_list.sort()
    lines = save_data('words_small.tcd', [word_list])
    print(('Words written in the dictionary (from the OLPC dictionary): ' + str(len(word_list))))
    return


def generate_ispell_dic(affixes_file, words_file, min_word_size, max_word_size):
    suffix_rules = {}
    read_suffix_rules(affixes_file, suffix_rules)
    words = {}
    read_words(words_file, words, suffix_rules)
    new_words = {}
    for word in words:
        if len(word) >= min_word_size and len(word) <= max_word_size:
            word = word.lower()
            word_no_accents = remove_accents(word)
            if word_no_accents not in new_words:
                new_words[word_no_accents] = word
            elif word == word_no_accents:
                new_words[word_no_accents] = word

    words = new_words
    word_list = []
    for (word_no_accent, word) in list(words.items()):
        word_list.append((word_no_accent, word))

    word_list.sort()
    word_list1 = []
    word_list2 = []
    for (word_no_accent, word) in word_list:
        word_list1.append(word_no_accent)
        word_list2.append(word)

    save_data('words_full.tcd', [word_list1, word_list2])
    print(('Words written in the dictionary (from the ispell dictionary): ' + str(len(word_list))))
    return


def read_suffix_rules(affixes_file, suffix_rules):
    lines = load_data(affixes_file, ';', True, False)
    suffixes = False
    for line in lines:
        line_text = line[0]
        line_text = line_text.strip()
        if len(line_text) > 0:
            if line_text[0] != '#':
                if suffixes or line_text == 'suffixes':
                    suffixes = True
            elif line_text.startswith('flag *'):
                k = line_text.index(':')
                name = line_text[6:k]
                rule = SuffixRule(name)
                suffix_rules[name] = rule
            else:
                entry = AffixEntry()
                rule.affix_entries.append(entry)
                def_index = line_text.find('>')
                if def_index == -1:
                    raise Exception("Expecting '>' in line: " + line_text)
                end_line = line_text.find('#', def_index)
                if end_line == -1:
                    end_line = len(line_text)
                read_conditions(line_text[0:def_index].strip(), entry)
                replace_rule = line_text[def_index + 1:end_line].strip()
                sep = replace_rule.find(',')
                if sep == -1:
                    entry.add_characters = get_word_with_accents(replace_rule)
                elif replace_rule[0] != '-':
                    raise Exception("'-' expected after '>' in line: " + line_text)
                entry.strip_characters = get_word_with_accents(replace_rule[1:sep].strip())
                entry.add_characters = get_word_with_accents(replace_rule[sep + 1:].strip())
                entry.add_characters = entry.add_characters.lower()

    return


def read_conditions(condition_text, entry):
    for i in range(len(entry.condition)):
        entry.condition[i] = 0

    if condition_text == '.':
        entry.condition_count = 0
        return
    neg = False
    group = False
    end = False
    chars = []
    num = 0
    accent = False
    for c in condition_text:
        if c == "'":
            accent = True
            continue
        elif accent:
            c = get_char_with_accent(c, condition_text)
            accent = False
        if c == '[':
            group = True
        elif c == '^' and group:
            neg = True
        elif c == ']':
            end = True
        elif group:
            chars.append(c)
        elif c != ' ' and c != '\t':
            end = True
        if end:
            if group:
                if neg:
                    for i in range(len(entry.condition)):
                        entry.condition[i] = entry.condition[i] | 1 << num

                    for ch in chars:
                        entry.condition[ord(ch)] = entry.condition[ord(ch)] & ~(1 << num)

                else:
                    for ch in chars:
                        entry.condition[ord(ch)] = entry.condition[ord(ch)] | 1 << num

                group = False
                neg = False
                chars = []
            elif c == '.':
                for i in range(len(entry.condition)):
                    entry.condition[i] = entry.condition[i] | 1 << num

            else:
                entry.condition[ord(c)] = entry.condition[ord(c)] | 1 << num
            end = False
            num += 1

    entry.condition_count = num
    return


def read_words(words_file, words, suffix_rules):
    lines = load_data(words_file, ';', True, False)
    for line in lines:
        line_text = line[0]
        add_word(line_text, words, suffix_rules)

    return


def get_word_with_accents(word):
    start = 0
    while start < len(word):
        k = word.find("'", start)
        if k == -1:
            break
        else:
            word = word[0:k] + get_char_with_accent(word[k + 1], word) + word[k + 2:]
            start = k + 1

    return word


def get_char_with_accent(c, text):
    if c == 'A':
        return 'Á'
    elif c == 'a':
        return 'á'
    elif c == 'E':
        return 'É'
    elif c == 'e':
        return 'é'
    elif c == 'I':
        return 'Í'
    elif c == 'i':
        return 'í'
    elif c == 'O':
        return 'Ó'
    elif c == 'o':
        return 'ó'
    elif c == 'U':
        return 'Ú'
    elif c == 'u':
        return 'ú'
    elif c == 'N':
        return 'Ñ'
    elif c == 'n':
        return 'ñ'
    else:
        raise Exception("Cannot add accent to char '" + c + "' in text '" + text + "'")
    return


def remove_accents(word):
    return word.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')


def add_word(line_text, words, suffix_rules):
    index = line_text.find('/')
    if index != -1:
        word = get_word_with_accents(line_text[0:index])
        affix_keys = line_text[index + 1:]
    else:
        word = get_word_with_accents(line_text)
        affix_keys = ''
    expanded_words = expand_word(word, affix_keys, suffix_rules)
    for w in expanded_words:
        if w not in words:
            words[w] = w

    return


def expand_word(word, affix_keys, suffix_rules):
    words = [
     word]
    for key in affix_keys:
        if key in suffix_rules:
            rule = suffix_rules[key]
            word_with_suffixes = add_suffix(word, rule)
            for w in word_with_suffixes:
                words.append(w)

    return words


def add_suffix(word, rule):
    words = []
    word_upper = word.upper()
    match_condition = False
    for entry in rule.affix_entries:
        if len(word_upper) >= entry.condition_count:
            pass_count = 0
            for i in range(entry.condition_count):
                c = word_upper[len(word_upper) - entry.condition_count + i]
                if entry.condition[ord(c)] & 1 << i == 1 << i:
                    pass_count += 1
                else:
                    break

            if pass_count == entry.condition_count:
                match_condition = True
                remove_letters = 0
                if len(entry.strip_characters) > 0:
                    if word_upper.endswith(entry.strip_characters):
                        remove_letters = len(entry.strip_characters)
                    else:
                        raise Exception("word '" + word + "' should ends with '" + entry.strip_characters + "' to add prefix '" + entry.add_characters + "'")
                temp_len = len(word) - remove_letters
                temp_word = word[0:temp_len]
                temp_word += entry.add_characters
                if temp_word != word:
                    words.append(temp_word)

    return words


class SuffixRule:

    def __init__(self, name):
        self.name = name
        self.allow_combine = False
        self.affix_entries = []
        return


class AffixEntry:

    def __init__(self):
        self.strip_characters = ''
        self.add_characters = ''
        self.condition = [0 for i in range(256)]
        self.condition_count = 0
        return


