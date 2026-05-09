import matplotlib.pyplot as plt

# Valores do exercício
valores = [1, 4, 9, 16, 25]

# Criar o gráfico de linhas
plt.plot(valores, color='green')

# Adicionar título e nomes aos eixos
plt.title('Gráfico de Linha')
plt.xlabel('Índice')
plt.ylabel('Valor')

plt.show()