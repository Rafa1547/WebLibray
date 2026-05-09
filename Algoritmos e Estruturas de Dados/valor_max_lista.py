b=[1,4,2,6,4,2]

def maximo(lista):
    maior=lista[0]
    for x in lista[1:]:
        maior=max(maior, x)
    return (maior)

print(maximo(b))