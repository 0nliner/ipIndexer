import itertools


class IPV4Addr:
    def __init__(self, a=0, b=0, c=0, d=0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    @classmethod
    def parse_from_string(cls, string: str):
        a, b, c, d = string.split(".")
        IPV4Addr(a, b, c, d)

    def __repr__(self):
        """
        переводит объект в строку
        :return:
        """
        def repr_unit(val) -> str:
            # проверка значения на range
            if not val in range(0, 256):
                raise ValueError(f"Value of ip chunk is {val}. Should be in range 0 <= x <= 255")

            string_repr = str(val)
            return string_repr

        return "".join(f"{repr_unit(val)}." for val in [self.a, self.b, self.c, self.d])[:-1]

    def __iter__(self):
        # итерируемся справа налево
        yield repr(self)
        for index, key in enumerate(["d", "c", "b", "a"]):
            while True:
                value = getattr(self, key)
                if 0 <= value < 254:
                    setattr(self, key, value+1)
                    yield repr(self)

                elif value == 254:
                    setattr(self, key, value+1)
                    yield repr(self)
                    break
        yield repr(self)


if __name__ == "__main__":
    ip_gen = IPV4Addr()
    for ip in ip_gen:
        print(ip)
