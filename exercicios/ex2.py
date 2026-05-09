import numpy as np

temperaturas = np.random.normal(20,5,365)

dias_quentes = temperaturas[temperaturas > 30]
qtd_dias_quentes = len(dias_quentes)
percentagem_quentes = (qtd_dias_quentes / 365) * 100

dias_frios = temperaturas[temperaturas < 10]
qtd_dias_frios = len(dias_frios)

temp_max = temperaturas.max()
temp_min = temperaturas.min()

print(f"Dias com >30ºC: {qtd_dias_quentes}")
print(f"Dias com <10ºC: {qtd_dias_frios}")
print(f"Percentagem de dias muito quentes: {percentagem_quentes:.2f}%")
print(f"Temperatura máxima do ano: {temp_max:.2f}ºC")
print(f"Temperatura mínima do ano: {temp_min:.2f}ºC")