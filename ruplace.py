import cli_ui as ui
import re
from inflection import camelize, underscore, dasherize


def screamize(x):
    return camelize(x).upper()


def ruplace(kind, input, pattern, replacement):
    if kind == "substring":
        input_fragments, output_fragments = get_fragments_substring(
            input, pattern, replacement
        )
    elif kind == "subvert":
        input_fragments, output_fragments = get_fragments_subvert(
            input, pattern, replacement
        )
    elif kind == "regex":
        regex = re.compile(pattern)
        input_fragments, output_fragments = get_fragments_regex(
            input, regex, replacement
        )
    output = get_output(input, input_fragments, output_fragments)
    print_red(input, input_fragments)
    print_green(output, output_fragments)
    return output


def get_fragments_substring(input, pattern, replacement):
    input_fragments = []
    output_fragments = []

    input_index = 0
    output_index = 0
    buff = input
    while True:
        pos = buff.find(pattern)
        if pos == -1:
            break
        input_index += pos
        output_index += pos
        input_fragments.append((input_index, pattern))
        output_fragments.append((output_index, replacement))
        buff = buff[input_index + len(pattern) :]
        input_index += len(pattern)
        output_index += len(replacement)

    return (input_fragments, output_fragments)


def subvert(buff, patterns, replacements):
    candidates = []
    best_pos = len(buff)
    best_pattern_index = None
    for i, pattern in enumerate(patterns):
        pos = buff.find(pattern)
        if pos != -1 and pos < best_pos:
            best_pos = pos
            best_pattern_index = i
    if best_pattern_index is None:
        return -1, None, None
    else:
        return best_pos, patterns[best_pattern_index], replacements[best_pattern_index]


def get_fragments_subvert(input, pattern, replacement):
    input_fragments = []
    output_fragments = []

    patterns = []
    replacements = []
    funcs = [camelize, underscore, dasherize, screamize]
    for func in funcs:
        patterns.append(func(pattern))
        replacements.append(func(replacement))

    input_index = 0
    output_index = 0
    buff = input
    while True:
        pos, pattern, replacement = subvert(buff, patterns, replacements)
        if pos == -1:
            break
        input_index += pos
        output_index += pos
        input_fragments.append((input_index, pattern))
        output_fragments.append((output_index, replacement))
        buff = buff[input_index + len(pattern) :]
        input_index += len(pattern)
        output_index += len(replacement)

    return (input_fragments, output_fragments)


def get_fragments_regex(input, regex, replacement):
    input_fragments = []
    output_fragments = []

    input_index = 0
    output_index = 0
    buff = input
    while True:
        match = regex.search(buff)
        if match is None:
            break
        group = match.group()
        input_index += match.start()
        output_index += match.start()
        input_fragments.append((input_index, group))
        new_string = regex.sub(replacement, group)
        output_fragments.append((output_index, new_string))
        buff = buff[input_index + len(group) :]
        input_index += len(group)
        output_index += len(new_string)

    return (input_fragments, output_fragments)


def get_output(input, input_fragments, output_fragments):
    current_index = 0
    output = ""
    for (in_index, in_substring), (out_index, out_substring) in zip(
        input_fragments, output_fragments
    ):
        output += input[current_index:in_index]
        output += out_substring
        current_index = in_index + len(in_substring)
    output += input[current_index:]
    return output


def print_red(input, input_fragments):
    ui.info(ui.red, "--- ", end="")
    current_index = 0
    for (in_index, in_substring) in input_fragments:
        ui.info(input[current_index:in_index], end="")
        ui.info(ui.red, ui.underline, in_substring, end="")
        current_index = in_index + len(in_substring)
    ui.info(input[current_index:])


def print_green(output, output_fragments):
    ui.info(ui.green, "+++ ", end="")
    current_index = 0
    for (out_index, out_substring) in output_fragments:
        ui.info(output[current_index:out_index], end="")
        ui.info(ui.green, ui.underline, out_substring, end="")
        current_index = out_index + len(out_substring)
    ui.info(output[current_index:])