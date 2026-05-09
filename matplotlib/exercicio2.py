import matplotlib.pyplot as plt

# Criar as listas: x de 1 até 15, e y com os quadrados desses números
x = list(range(1, 16))
y = [n**2 for n in x]

# Criar o gráfico de linhas
# Cor roxa (purple), marcadores em forma de bolinha ('o')
plt.plot(x, y, color='purple', marker='o')

# Adicionar título e nomes aos eixos
plt.title('Quadrados')
plt.xlabel('Número')
plt.ylabel('Quadrado')

# Ativar a grelha no fundo do gráfico
plt.grid(True)

# Mostrar o gráfico
plt.show()