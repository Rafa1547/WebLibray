import matplotlib.pyplot as plt

x = list(range(-20, 21))

y = []
for n in x:
    if n < 0:
        y.append(abs(n)**2)  
    elif n == 0:
        y.append(0)          
    else:
        y.append(n**3)       

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

ax1.plot(x, y, color='darkblue', marker='d')
ax1.set_title('Quadrados (Negativos) e Cubos (Positivos)')
ax1.set_xlabel('Número Original')
ax1.set_ylabel('Valor Calculado')
ax1.grid(True)

y_barras = []
for i in range(len(x)):
    if x[i] < 0:
        y_barras.append(-y[i])
    else:
        y_barras.append(y[i])

ax2.bar(x, y_barras, color='magenta')
ax2.set_title('Quadrados (Negativos) e Cubos (Positivos)')
ax2.set_xlabel('Número Original')
ax2.set_ylabel('Valor Calculado')

cores = []
for n in x:
    if n < 0:
        cores.append('red')
    elif n > 0:
        cores.append('green')
    else:
        cores.append('black')

ax3.scatter(x, y, c=cores)
ax3.set_title('Quadrados (Negativos) e Cubos (Positivos)')
ax3.set_xlabel('Número Original')
ax3.set_ylabel('Valor Calculado')

plt.tight_layout()

plt.show()