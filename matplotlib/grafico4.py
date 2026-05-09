import matplotlib.pyplot as plt
import math
import random

random.seed(42)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 8))
fig.suptitle('Subplots — 4 gráficos', fontsize=14, fontweight='bold')

# y = x²
x1 = [i * 0.5 for i in range(11)]
y1 = [v**2 for v in x1]
ax1.plot(x1, y1, color='blue', marker='o', markersize=6, markerfacecolor='white')
ax1.set_title('y = x²')
ax1.set_xlabel('x')
ax1.set_ylabel('y')

# scatter
x2 = [random.uniform(0, 10) for _ in range(30)]
y2 = [random.uniform(0, 10) for _ in range(30)]
ax2.scatter(x2, y2, color='red', s=40)
ax2.set_title('Dispersão (scatter)')

# barras
categorias = ['A', 'B', 'C', 'D', 'E']
valores = [3, 7, 5, 9, 4]
cores = ['blue', 'red', 'green', 'orange', 'purple']
ax3.bar(categorias, valores, color=cores)
ax3.set_title('Barras coloridas')

# seno e cosseno
x4 = [i * 0.05 for i in range(126)]
ax4.plot(x4, [math.sin(v) for v in x4], color='red', label='sin(x)')
ax4.plot(x4, [math.cos(v) for v in x4], color='blue', label='cos(x)')
ax4.axhline(y=0, color='black', linewidth=0.8)
ax4.set_title('Seno e Cosseno')
ax4.legend()

plt.tight_layout()
plt.show()