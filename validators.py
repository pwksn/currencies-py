class Validators:
    def __init__(self):
        pass

    def is_value_correct(self, value):
        is_value_float = self.is_float(value)
        if is_value_float:
            return float(value) > 0
        return False

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
