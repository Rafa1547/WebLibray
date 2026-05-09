import matplotlib.pyplot as plt

horas  = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
lisboa = [12, 11, 10, 10, 11, 14, 18, 22, 25, 26, 24, 20, 15]
porto  = [8, 7, 6, 5, 6,  9, 13, 17, 20, 21, 19, 15, 10]

plt.figure(figsize=(11, 6))

plt.plot(horas, lisboa, color='red', marker='o', markersize=5, linewidth=1.8, label='Lisboa')
plt.plot(horas, porto, color='blue', marker='s', markersize=5, markerfacecolor='white', markeredgecolor='blue', linewidth=1.8, linestyle='--', label='Porto')
plt.axhline(y=15, color='gray', linestyle=':', linewidth=1, label='Ref: 15°C')

plt.title('temperatura ao longo do dia', fontweight='bold')
plt.xlabel('hora do dia')
plt.ylabel('temperatura (°C)')
plt.xlim(0, 24)
plt.ylim(0, 30)
plt.xticks(horas)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()