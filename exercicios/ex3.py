import numpy as np

temperaturas = np.random.normal(22, 4, 1000)
co2 = np.random.normal(400, 50, 1000)

criticos_temp = (temperaturas > 28) & (co2 > 450)
temps_criticas = temperaturas[criticos_temp]
co2_critico = co2[criticos_temp]
qtd_criticos = len(temps_criticas)
percentagem_criticos = (qtd_criticos / 1000) * 100

media_temp_crit = temps_criticas.mean()
desvio_temp_crit = temps_criticas.std()

media_co2_crit = co2_critico.mean()
desvio_co2_crit = co2_critico.std()

print(f"quantidade de medições críticas: {qtd_criticos}")
print(f"percentagem de medições críticas: {percentagem_criticos:.2f}%")
print(f"media das temperaturas: {media_temp_crit:.2f}ºC")
print(f"desvio padrão das temperaturas: {desvio_temp_crit:.2f}")
print(f"media do CO2: {media_co2_crit:.2f}ppm")
print(f"desvio padrão do CO2: {desvio_co2_crit:.2f}")

