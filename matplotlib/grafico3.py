import matplotlib.pyplot as plt
import math
import random

random.seed(7)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 7))
fig.suptitle('4 gráficos', fontsize=13)

# linha com ruído
x1 = list(range(20))
y1 = [v + random.uniform(-2, 2) for v in x1]
ax1.plot(x1, y1, color='blue', marker='o', markersize=4, linewidth=1.5)
ax1.set_title('linha com ruído')
ax1.set_xlabel('x')
ax1.set_ylabel('y')

# barras horizontais
nomes = ['Ana', 'Bruno', 'Carlos', 'Diana', 'Eva']
pontos = [random.randint(40, 100) for _ in nomes]
ax2.barh(nomes, pontos, color='green')
ax2.set_title('pontuações')
ax2.set_xlabel('pontos')

# scatter com tamanhos variáveis
x3 = [random.uniform(0, 10) for _ in range(40)]
y3 = [random.uniform(0, 10) for _ in range(40)]
tamanhos = [random.randint(20, 200) for _ in range(40)]
ax3.scatter(x3, y3, s=tamanhos, color='red', alpha=0.6)
ax3.set_title('scatter com tamanhos')

# seno 
x4 = [i * 0.1 for i in range(80)]
y4 = [math.sin(v) * math.exp(-v * 0.1) for v in x4]
ax4.plot(x4, y4, color='purple', linewidth=1.8)
ax4.axhline(y=0, color='black', linewidth=0.6)
ax4.set_title('seno')

plt.tight_layout()
plt.show()