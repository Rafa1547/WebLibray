b=[1,4,2,6,4,2]

def minimo(lista):
    menor=lista[0]
    for x in lista[1:]:
        menor=min(menor, x)
    return (menor)

print(minimo(b))