from .errors import ExpectedClosingQuote

class ArgumentReader:
    def __init__(self, buffer):
        self.index = 0
        self.buffer = buffer
        self.legnth = len(buffer)

    def argument(self):
        pos = 0
        in_quotes = False
        result = ""

        while True:
            try:
                current = self.buffer[self.index + pos]
                pos += 1
                if current == " " and result.strip(" ") and not in_quotes:
                    self.index += pos
                    break
                elif current == '"':
                    in_quotes = True if not in_quotes else False
                else:
                    result += current

            except IndexError:
                self.index = self.legnth
                if in_quotes:
                    raise ExpectedClosingQuote() from None

                if not result.strip(" "):
                    result = ""
                break

        return result

    def keyword_argument(self):
        result = self.buffer[self.index:]
        self.index = self.legnth

        if not result.strip(" "):
            return ""
        return result

    def extras(self):
        arguments = []
        while True:
            argument = self.argument()
            if argument:
                arguments.append(argument)
            else:
                break

        return arguments
