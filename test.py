import re


def find_group(text, key):
    pattern = fr"{key}\*(\d+)\((-?\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*)\)"
    match = re.search(pattern, text)
    if match:
        n = int(match.group(1))
        x = int(match.group(2))/(10**n) if n != 0 else int(match.group(2))
        y = int(match.group(3))/(10**n) if n != 0 else int(match.group(3))
        z = int(match.group(4))/(10**n) if n != 0 else int(match.group(4))
        return [x, y, z]
    return []


s = 'M*0(20,10,23)'

print(find_group(s, 'M'))