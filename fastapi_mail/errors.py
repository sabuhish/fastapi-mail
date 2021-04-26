class ConnectionErrors(Exception):

    def __init__(self, expression):
        self.expression = expression


class WrongFile(Exception):

    def __init__(self, expression):
        self.expression = expression


class PydanticClassRequired(Exception):

    def __init__(self, expression):
        self.expression = expression


class TemplateFolderDoesNotExist(Exception):

    def __init__(self, expression):
        self.expression = expression
