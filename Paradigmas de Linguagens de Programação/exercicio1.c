#include <stdio.h>
#include <math.h>

#define PI 3.14159265358979323846
#define E  2.71828182845904523536

int main() {
    int opcao;
    double x, y, r;
    int nx, ny, i, f;

    do {
        printf("\n===== CALCULADORA =====\n");
        printf(" 1  - Soma\n");
        printf(" 2  - Subtracao\n");
        printf(" 3  - Multiplicacao\n");
        printf(" 4  - Divisao\n");
        printf(" 5  - Resto da divisao (inteiros)\n");
        printf(" 6  - Potencia (x^y)\n");
        printf(" 7  - Raiz quadrada\n");
        printf(" 8  - Raiz cubica\n");
        printf(" 9  - Seno (graus)\n");
        printf("10  - Cosseno (graus)\n");
        printf("11  - Tangente (graus)\n");
        printf("12  - Seno (radianos)\n");
        printf("13  - Cosseno (radianos)\n");
        printf("14  - Tangente (radianos)\n");
        printf("15  - Logaritmo base 10 (log10)\n");
        printf("16  - Logaritmo natural (ln)\n");
        printf("17  - e^x\n");
        printf("18  - 10^x\n");
        printf("19  - Mostrar valor de PI\n");
        printf("20  - Mostrar valor de e\n");
        printf("21  - Fatorial (n!)\n");
        printf("22  - Valor absoluto\n");
        printf("23  - Arredondar para cima (ceil)\n");
        printf("24  - Arredondar para baixo (floor)\n");
        printf("25  - Converter graus para radianos\n");
        printf(" 0  - Sair\n");
        printf("Escolha uma opcao: ");

        if (scanf("%d", &opcao) != 1) {
            printf("Entrada invalida.\n");
            return 1;
        }

        switch (opcao) {
            case 1:
                printf("Introduza dois numeros: ");
                scanf("%lf %lf", &x, &y);
                r = x + y;
                printf("Resultado: %.6lf\n", r);
                break;

            case 2:
                printf("Introduza dois numeros: ");
                scanf("%lf %lf", &x, &y);
                r = x - y;
                printf("Resultado: %.6lf\n", r);
                break;

            case 3:
                printf("Introduza dois numeros: ");
                scanf("%lf %lf", &x, &y);
                r = x * y;
                printf("Resultado: %.6lf\n", r);
                break;

            case 4:
                printf("Introduza dois numeros (numerador denominador): ");
                scanf("%lf %lf", &x, &y);
                if (y == 0) {
                    printf("Erro: divisao por zero!\n");
                } else {
                    r = x / y;
                    printf("Resultado: %.6lf\n", r);
                }
                break;

            case 5:
                printf("Introduza dois inteiros (a b): ");
                scanf("%d %d", &nx, &ny);
                if (ny == 0) {
                    printf("Erro: divisao por zero!\n");
                } else {
                    printf("Resto: %d\n", nx % ny);
                }
                break;

            case 6:
                printf("Introduza base e expoente (x y): ");
                scanf("%lf %lf", &x, &y);
                r = pow(x, y);
                printf("Resultado: %.6lf\n", r);
                break;

            case 7:
                printf("Introduza um numero: ");
                scanf("%lf", &x);
                if (x < 0) {
                    printf("Erro: raiz de numero negativo!\n");
                } else {
                    r = sqrt(x);
                    printf("Resultado: %.6lf\n", r);
                }
                break;

            case 8:
                printf("Introduza um numero: ");
                scanf("%lf", &x);
                r = cbrt(x);
                printf("Resultado: %.6lf\n", r);
                break;

            case 9:
                printf("Introduza o angulo em graus: ");
                scanf("%lf", &x);
                r = sin(x * PI / 180.0);
                printf("Seno(graus): %.6lf\n", r);
                break;

            case 10:
                printf("Introduza o angulo em graus: ");
                scanf("%lf", &x);
                r = cos(x * PI / 180.0);
                printf("Cosseno(graus): %.6lf\n", r);
                break;

            case 11:
                printf("Introduza o angulo em graus: ");
                scanf("%lf", &x);
                r = tan(x * PI / 180.0);
                printf("Tangente(graus): %.6lf\n", r);
                break;

            case 12:
                printf("Introduza o angulo em radianos: ");
                scanf("%lf", &x);
                r = sin(x);
                printf("Seno(radianos): %.6lf\n", r);
                break;

            case 13:
                printf("Introduza o angulo em radianos: ");
                scanf("%lf", &x);
                r = cos(x);
                printf("Cosseno(radianos): %.6lf\n", r);
                break;

            case 14:
                printf("Introduza o angulo em radianos: ");
                scanf("%lf", &x);
                r = tan(x);
                printf("Tangente(radianos): %.6lf\n", r);
                break;

            case 15:
                printf("Introduza um numero positivo: ");
                scanf("%lf", &x);
                if (x <= 0) {
                    printf("Erro: log10 definido apenas para numeros positivos!\n");
                } else {
                    r = log10(x);
                    printf("log10(%.6lf) = %.6lf\n", x, r);
                }
                break;

            case 16:
                printf("Introduza um numero positivo: ");
                scanf("%lf", &x);
                if (x <= 0) {
                    printf("Erro: ln definido apenas para numeros positivos!\n");
                } else {
                    r = log(x);
                    printf("ln(%.6lf) = %.6lf\n", x, r);
                }
                break;

            case 17:
                printf("Introduza x para e^x: ");
                scanf("%lf", &x);
                r = exp(x);
                printf("e^%.6lf = %.6lf\n", x, r);
                break;

            case 18:
                printf("Introduza x para 10^x: ");
                scanf("%lf", &x);
                r = pow(10.0, x);
                printf("10^%.6lf = %.6lf\n", x, r);
                break;

            case 19:
                printf("PI = %.15lf\n", PI);
                break;

            case 20:
                printf("e = %.15lf\n", E);
                break;

            case 21:
                printf("Introduza um inteiro nao negativo: ");
                scanf("%d", &nx);
                if (nx < 0) {
                    printf("Erro: fatorial de numero negativo!\n");
                } else {
                    f = 1;
                    for (i = 1; i <= nx; i++) {
                        f *= i;
                    }
                    printf("%d! = %d\n", nx, f);
                }
                break;

            case 22:
                printf("Introduza um numero: ");
                scanf("%lf", &x);
                r = fabs(x);
                printf("|%.6lf| = %.6lf\n", x, r);
                break;

            case 23:
                printf("Introduza um numero: ");
                scanf("%lf", &x);
                r = ceil(x);
                printf("ceil(%.6lf) = %.6lf\n", x, r);
                break;

            case 24:
                printf("Introduza um numero: ");
                scanf("%lf", &x);
                r = floor(x);
                printf("floor(%.6lf) = %.6lf\n", x, r);
                break;

            case 25:
                printf("Introduza o angulo em graus: ");
                scanf("%lf", &x);
                r = x * PI / 180.0;
                printf("%.6lf graus = %.6lf radianos\n", x, r);
                break;

            case 0:
                printf("A sair da calculadora...\n");
                break;

            default:
                printf("Opcao invalida. Tente novamente.\n");
        }

    } while (opcao != 0);

    return 0;
}