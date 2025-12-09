import re

def get_angle_from_key(s):
    """
    Extract two non-negative numbers (ints or floats) from a string like '(25, 135)'.
    
    Returns a tuple of floats: (num1, num2)
    """
    # Match numbers like 25, 3.14, 0.5
    pattern = r'\d*\.?\d+'
    numbers = re.findall(pattern, s)
    
    if len(numbers) != 2:
        raise ValueError(f"Expected 2 numbers in string, found {len(numbers)}: {s}")
    
    return float(numbers[0]), float(numbers[1])