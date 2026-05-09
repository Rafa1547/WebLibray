import numpy as np

numeros = np.random.normal(loc=5, scale=2, size=500)

maior_que_7 = numeros[numeros > 7]

print("Array filtrado (valores > 7):")
print(maior_que_7)
print("\nQuantidade de valores > 7:", len(maior_que_7))