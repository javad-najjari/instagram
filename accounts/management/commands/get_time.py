import random



def get_time():
    a = random.choice(range(0, 3))
    b = random.choice(range(1, 13))
    c = random.choice(range(1, 30))
    d = random.choice(range(0, 24))
    e = random.choice(range(0, 60))
    f = random.choice(range(0, 60))

    if b < 10:
        b = f'0{str(b)}'
    if c < 10:
        c = f'0{str(c)}'
    if d < 10:
        d = f'0{str(d)}'
    if e < 10:
        e = f'0{str(e)}'
    if f < 10:
        f = f'0{str(f)}'

    a, b, c, d, e, f = str(a), str(b), str(c), str(d), str(e), str(f)
    my_time = f'202{a}-{b}-{c} {d}:{e}:{f}'
    return my_time

