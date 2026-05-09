/*
Numero: 2025116321
Nome: Rafael Pires
*/

#include <stdio.h>

int main() {
    int opcao, dias, idade, continuar;
    float preco_dia, preco_total, preco_com_desconto;
    int total_alugueres = 0;
    int total_dias = 0;
    float valor_total = 0.0;
    char resposta;

    do {
        // Solicitar tipo de veículo
        printf("Introduza qual e a categoria do veiculo a ser alugado:\n");
        printf("1 - Carro ligeiro\n");
        printf("2 - Moto\n");
        printf("3 - Autocarravana\n");
        printf("Opcao: ");
        scanf("%d", &opcao);

        // Validar opção
        while (opcao < 1 || opcao > 3) {
            printf("Opcao invalida! Introduza uma opcao valida (1-3): ");
            scanf("%d", &opcao);
        }

        // Definir preço por dia conforme o tipo de veículo
        switch (opcao) {
            case 1:
                preco_dia = 40.00;
                break;
            case 2:
                preco_dia = 20.00;
                break;
            case 3:
                preco_dia = 70.00;
                break;
        }

        // Solicitar duração do aluguer
        printf("Introduza a duracao total do aluguer (em dias): ");
        scanf("%d", &dias);

        // Validar dias
        while (dias <= 0) {
            printf("Numero de dias invalido! Introduza um numero positivo: ");
            scanf("%d", &dias);
        }

        // Solicitar idade do condutor
        printf("Introduza a idade do condutor (em anos): ");
        scanf("%d", &idade);

        // Validar idade
        while (idade <= 0 || idade > 150) {
            printf("Idade invalida! Introduza uma idade valida: ");
            scanf("%d", &idade);
        }

        // Calcular preço total
        preco_total = preco_dia * dias;

        // Aplicar desconto de 20% se aluguer superior a 7 dias
        if (dias > 7) {
            preco_com_desconto = preco_total * 0.80;
        } else {
            preco_com_desconto = preco_total;
        }

        // Determinar nome do veículo para exibição
        switch (opcao) {
            case 1:
                if (dias == 1) {
                    printf("\nPara um aluguer de %d dia de um Carro ligeiro:\n", dias);
                } else {
                    printf("\nPara um aluguer de %d dias de um Carro ligeiro:\n", dias);
                }
                break;
            case 2:
                if (dias == 1) {
                    printf("\nPara um aluguer de %d dia de uma Mota:\n", dias);
                } else {
                    printf("\nPara um aluguer de %d dias de uma Mota:\n", dias);
                }
                break;
            case 3:
                if (dias == 1) {
                    printf("\nPara um aluguer de %d dia de uma Autocarravana:\n", dias);
                } else {
                    printf("\nPara um aluguer de %d dias de uma Autocarravana:\n", dias);
                }
                break;
        }

        // Mostrar resumo do aluguer
        printf("Preco por dia: %.2fEur\n", preco_dia);
        if (dias > 7) {
            printf("Desconto aplicado (20%%): %.2fEur\n", preco_total - preco_com_desconto);
            printf("Preco Total do aluguer: %.2fEur\n", preco_com_desconto);
        } else {
            printf("Preco Total do aluguer: %.2fEur\n", preco_com_desconto);
        }

        // Atualizar totais
        total_alugueres++;
        total_dias += dias;
        valor_total += preco_com_desconto;

        // Perguntar se deseja continuar
        printf("\nDeseja continuar (S/N)? ");
        scanf(" %c", &resposta);

        // Converter resposta para maiúscula e validar
        if (resposta >= 'a' && resposta <= 'z') {
            resposta = resposta - 32;
        }

        while (resposta != 'S' && resposta != 'N') {
            printf("Resposta invalida! Introduza S ou N: ");
            scanf(" %c", &resposta);
            if (resposta >= 'a' && resposta <= 'z') {
                resposta = resposta - 32;
            }
        }

        continuar = (resposta == 'S') ? 1 : 0;
        printf("\n");

    } while (continuar == 1);

    // Mostrar estatísticas finais
    printf("\n=== Resumo Final ===\n");
    printf("Numero total de alugueres: %d\n", total_alugueres);
    printf("Numero total de dias de alugueres: %d\n", total_dias);
    printf("Valor total dos alugueres: %.2fEur\n", valor_total);

    return 0;
}

