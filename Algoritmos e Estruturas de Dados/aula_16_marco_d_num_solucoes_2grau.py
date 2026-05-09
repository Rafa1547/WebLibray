a = float(input("a: "))
b = float(input("b: "))
c = float(input("c: "))

if a == 0:
    print("Não é equação de 2º grau (a tem de ser diferente de 0).")
else:
    delta = b**2 - 4 * a * c

    if delta > 0:
        print("2 soluções reais")
    elif delta == 0:
        print("1 solução real")
    else:
        print("0 soluções reais")

