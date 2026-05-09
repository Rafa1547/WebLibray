b=[1,4,2,6,4,2]

def produto(lista):
    total=1
    for x in lista[1:]:
        total=min(total, x)
    return (total)

print(produto(b))