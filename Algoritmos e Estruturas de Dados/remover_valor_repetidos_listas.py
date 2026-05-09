def eliminarrepetidos(lista):
    lista2=[]
    for x in lista:
        if not (x in lista2):
            lista2.append(x)
    return(lista2)

e=[1,3,2,5,4,1,5,4,2,3,4,5,1]

print(eliminarrepetidos(e))