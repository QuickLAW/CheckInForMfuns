class Headers():
    def __init__(self) -> None:
        self.headers = {}

    def set_header(self, key, value):
        self.headers[key] = value

    def del_header(self, key):
        del self.headers[key]