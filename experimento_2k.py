import pandas as pd
from itertools import combinations, product

def lerDadosEntrada():
    while True:
        try:
            numFatores = int(input("Digite o número de fatores (2 a 5): "))
            if 2 <= numFatores <= 5:
                break
            else:
                print("Número de fatores fora do intervalo.")
        except ValueError:
            print("Entrada inválida.")
    while True:
        try:
            numReplicacoes = int(input("Digite o número de replicações (1 a 3): "))
            if 1 <= numReplicacoes <= 3:
                break
            else:
                print("Número de replicações fora do intervalo.")
        except ValueError:
            print("Entrada inválida.")
    return numFatores, numReplicacoes

def gerar_sinais(numFatores):
    sinais_binarios = list(product([-1, 1], repeat=numFatores))
    return sinais_binarios

def tabela_sinais(numFatores):
    base = "ABCDE"[:numFatores]
    sinais = gerar_sinais(numFatores)

    dados = []
    for linha in sinais:
        linha_dict = {"I": 1}
        for fator, valor in zip(base, linha[::-1]):  
            linha_dict[fator] = valor
        dados.append(linha_dict)

    df = pd.DataFrame(dados)

    colunas_ordem = ["I"] + list(base)
    for r in range(2, numFatores + 1):
        for comb in combinations(base, r):
            nome = ''.join(comb)
            df[nome] = df[list(comb)].prod(axis=1)
            colunas_ordem.append(nome)
    return df, colunas_ordem

def coleta_respostas(tabela, numReplicacoes):
    respostas = []
    for r in range(numReplicacoes):
        tabela[f"R{r+1}"] = None

    for idx, linha in tabela.iterrows():
        print(f"\nTratamento {idx+1}: ", end='')
        print(', '.join([f"{col}={linha[col]}" for col in tabela.columns if col != "I"]))

        y = []
        for r in range(numReplicacoes):
            while True:
                try:
                    val = float(input(f"  Repetição {r+1}: "))
                    y.append(val)
                    tabela.at[idx, f"R{r+1}"] = val  
                    break
                except ValueError:
                    print("Valor inválido. Tente novamente.")
        respostas.append(y)
    return respostas


def calcula_efeitos(tabela, respostas, colunas_ordem, numReplicacoes):
    df_y = pd.DataFrame(respostas)
    medias = df_y.mean(axis=1)
    tabela["y"] = medias

    erros = {}
    for k in range(numReplicacoes):
        col = tabela[f"R{k+1}"]
        erro_col = col - tabela["y"]
        erros[f"e{k+1}"] = erro_col

    df_erros = pd.DataFrame(erros)
    tabela = pd.concat([tabela, df_erros], axis=1)

    SSE = df_erros.pow(2).sum().sum()

    todos_y = df_y.values.flatten()
    media_geral = todos_y.mean()
    SST = sum((val - media_geral)**2 for val in todos_y)

    efeitos = {}
    totais = {}

    for col in colunas_ordem:
        produto = (tabela[col] * tabela["y"])
        q = produto.sum() / len(tabela)
        SS = len(tabela) * q ** 2 * numReplicacoes
        efeitos[col] = {"efeito": q, "SS": SS}
        totais[col] = produto.sum()

    print("\n>>> RESULTADOS EXPERIMENTAIS <<<")
    print("Tabela Final com Médias e Erros:")
    print(tabela)

    print("Tabela de Efeitos: ")
    print("Colunas:   " + "  ".join(colunas_ordem))
    print("Total:     " + "  ".join(f"{totais[k]:.0f}" for k in colunas_ordem))
    print("Total/N:   " + "  ".join(f"{totais[k]/len(tabela):.0f}" for k in colunas_ordem))

    print("\nResultados:")
    print(f"Soma Total dos Quadrados (SST): {SST:.2f}")
    print(f"Soma dos Quadrados do Erro (SSE): {SSE:.2f}")

    for fator in colunas_ordem[1:]:
        val = efeitos[fator]
        perc = (val['SS'] / SST) * 100 if SST != 0 else 0
        print(f"{fator}: Efeito = {val['efeito']:.2f}, SS{fator} = {val['SS']:.2f}, Variação Explicada = {perc:.2f}%")

    return tabela, efeitos, SSE, SST

if __name__ == "__main__":
    numFatores, numReplicacoes = lerDadosEntrada()
    tabela, colunas_ordem = tabela_sinais(numFatores)
    respostas = coleta_respostas(tabela, numReplicacoes)
    tabela, efeitos, SSE, SST = calcula_efeitos(tabela, respostas, colunas_ordem, numReplicacoes)

    erro_percentual = (SSE / SST) * 100 if SST != 0 else 0
    print(f"Erro Total: {erro_percentual:.2f}%")
