import random



class Utils:
    @staticmethod
    def get_random_hex_color():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))