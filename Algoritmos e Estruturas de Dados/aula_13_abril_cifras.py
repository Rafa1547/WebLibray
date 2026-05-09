def rodar(k,c ):
    "rodar o caracter c por k posições"
    k = int(k)
    if c>='a' and c<='z':
        n=ord(c)-ord('a')
        return chr((n+k)%26+ord('a'))
    else:
        return c
def cifrar(k,texto):
    "cifrar o texto com o valor de k"
    k = int(k)
    mensagem = ""
    for c in texto:
        mensagem += rodar(k, c)
    return mensagem

def descodificar(k,texto):
    "descodificar o texto com o valor de k"
    k = int(k)
    mensagem = ""
    for c in texto:
        mensagem += rodar(-k, c)
    return mensagem

print(cifrar('3', 'ataque de madrugada'))
print(cifrar('5', 'texto para cifrar'))
print(descodificar('3', 'dwdtxh gh pdguxjdgd'))
print(descodificar('5', 'yjxyj ufwf ijxhtinknhfw'))