import re

from mistletoe.span_token import SpanToken


class Morse(SpanToken):
    """
    Morse code span token ("[morse:moe]").
    Generates morse code from a text.
    """

    @staticmethod
    def convert_to_morse_code(text):
        dit = 1
        dah = 2
        space = 3

        morse_code = {
            "a": [dit, dah],
            "b": [dah, dit, dit, dit],
            "c": [dah, dit, dah, dit],
            "d": [dah, dit, dit],
            "e": [dit],
            "f": [dit, dit, dah, dit],
            "g": [dah, dah, dit],
            "h": [dit, dit, dit, dit],
            "i": [dit, dit],
            "j": [dit, dah, dah, dah],
            "k": [dah, dit, dah],
            "l": [dit, dah, dit, dit],
            "m": [dah, dah],
            "n": [dah, dit],
            "o": [dah, dah, dah],
            "p": [dit, dah, dah, dit],
            "q": [dah, dah, dit, dah],
            "r": [dit, dah, dit],
            "s": [dit, dit, dit],
            "t": [dah],
            "u": [dit, dit, dah],
            "v": [dit, dit, dit, dah],
            "w": [dit, dah, dah],
            "x": [dah, dit, dit, dah],
            "y": [dah, dit, dah, dah],
            "z": [dah, dah, dit, dit],
            "ä": [dit, dah, dit, dah],
            "ö": [dah, dah, dah, dit],
            "ü": [dit, dit, dah, dah],
            "ß": [dit, dit, dit, dah, dah, dit, dit],
            "0": [dah, dah, dah, dah, dah],
            "1": [dit, dah, dah, dah, dah],
            "2": [dit, dit, dah, dah, dah],
            "3": [dit, dit, dit, dah, dah],
            "4": [dit, dit, dit, dit, dah],
            "5": [dit, dit, dit, dit, dit],
            "6": [dah, dit, dit, dit, dit],
            "7": [dah, dah, dit, dit, dit],
            "8": [dah, dah, dah, dit, dit],
            "9": [dah, dah, dah, dah, dit],
            ".": [dit, dah, dit, dah, dit, dah],
            ",": [dah, dah, dit, dit, dah, dah],
            ":": [dah, dah, dah, dit, dit, dit],
            ";": [dah, dit, dah, dit, dah, dit],
            "?": [dit, dit, dah, dah, dit, dit],
            "!": [dah, dit, dah, dit, dah, dah],
            "-": [dah, dit, dit, dit, dit, dah],
            "_": [dit, dit, dah, dah, dit, dah],
            "(": [dah, dit, dah, dah, dit],
            ")": [dah, dit, dah, dah, dit, dah],
            "'": [dit, dah, dah, dah, dah, dit],
            "=": [dah, dit, dit, dit, dah],
            "+": [dit, dah, dit, dah, dit],
            "/": [dah, dit, dit, dah, dit],
            "@": [dit, dah, dah, dit, dah, dit],
            "ar": [dit, dah, dit, dah, dit],
            "bk": [dah, dit, dit, dit, dah, dit, dah],
            "sk": [dit, dit, dit, dah, dit, dah],
            "correction": [dit, dit, dit, dit, dit, dit, dit, dit],
            " ": [space],
        }

        # Prosigns (e.g. "ar", "bk", "sk", "correction") are stored as multi-
        # character keys whose dit/dah list already has no gap between the
        # individual letters - that's what makes them a prosign rather than
        # two separate letters. They must therefore be matched as a whole
        # "word", not character by character, otherwise they're never found
        # and get split into individual letters with an (incorrect) gap
        # between them.
        prosigns = {key: value for key, value in morse_code.items() if len(key) > 1}

        result = []

        # Split into words and whitespace, keeping the whitespace as its own
        # token so word gaps are preserved exactly as before.
        for token in re.split(r"(\s)", text):
            if not token:
                continue

            if token.isspace():
                for char in token:
                    if char in morse_code:
                        result.append(morse_code[char])
                continue

            if token.lower() in prosigns:
                result.append(prosigns[token.lower()])
                continue

            for char in token:
                if char.lower() in morse_code:
                    result.append(morse_code[char.lower()])

        return result

    parse_inner = False
    pattern = re.compile(r"\[morse:\s*([^\]]+)\]")
