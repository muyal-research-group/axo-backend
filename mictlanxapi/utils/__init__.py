import random
def get_random_hex_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))


    # r = random.randint(0, 255)  # Red
    # g = random.randint(0, 255)  # Green
    # b = random.randint(0, 255)  # Blue
    # return (r, g, b)
