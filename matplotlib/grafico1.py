import matplotlib.pyplot as plt
import numpy as np

x = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]

y_red    = [2, 4, 3, 4,   1, 4.5, 6, 4,   3]
y_blue   = [3, 4, 5, 3,   2, 4.5, 7, 4,   4]
y_laranja= [4, 2, 2, 3.5, 5, 5,   3, 2,   6]
y_roxo   = [4, 3, 2, 4,   6, 4.5, 3, 4.5, 5]

plt.figure(figsize=(9, 5))

plt.plot(x, y_red,     color='red',              label='Nome: red')
plt.plot(x, y_blue,    color='blue',             label='Nome: blue')
plt.plot(x, y_laranja, color='#E67E22',          label='HEX: laranja')
plt.plot(x, y_roxo,    color=(0.5, 0.1, 0.6),   label='RGB: roxo')

plt.title('Exemplos de cores')
plt.xlabel('X')
plt.ylim(1, 8)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()