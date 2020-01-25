class NotAvilableService(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class TypeExecption(TypeError):

    def __init__(self, expression):
        self.expression = expression

class ConnectionErrors(Exception):

    def __init__(self, expression):
        self.expression = expression


class WrongPort(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class WrongFormat(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class WrongFile(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
