def find_valence(x, a, b):
  x_min = -4
  x_max = 4

  return a + ((x - x_min) * (b - a) / (x_max - x_min))

print(find_valence(-2.3, -1, 1))
