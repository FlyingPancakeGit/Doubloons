def ease_in_ease_out_cubic(time):
    if time < 0.5:
        return 4 * (time ** 3)
    else:
        return 1 - (((-2 * time + 2) ** 3) / 2)

def ease_out_quadratic(time):
    return -time * (time - 2)