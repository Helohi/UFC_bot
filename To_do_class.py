class ToDo(dict):
    def append(self, **kwargs):
        for key in kwargs:
            self[key] = kwargs[key]
        return self.func(self)

    def append_function(self, func):
        self.func = func
