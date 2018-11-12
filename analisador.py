# -*- coding: utf-8 -*-


# Função responsável pela análise dos resultados da execução:
def analisar(perspectiva, positivo, negativo, fps):
    # Mensagem no dump notificando o fim da execução:
    print("Fim de execução.")

    # Gera as strings referentes aos vetores da perspectiva horizontal:
    if (perspectiva == "horizontal"):
        vetor_positivo = "para a direita"
        vetor_negativo = "para a esquerda"

    # Gera as strings referentes aos vetores da perspectiva vertical:
    elif(perspectiva == "vertical"):
        vetor_positivo = "subindo"
        vetor_negativo = "descendo"

    # Demonstra no dump as estatísticas finais:
    print("Tráfego %s: %d pessoas;" %(vetor_positivo, positivo))
    print("Tráfego %s: %d pessoas;" %(vetor_negativo, negativo))
    print ("Pessoas detectadas: %d" %(positivo + negativo))

    # Para o relógio e o demonstra no dump junto com a taxa média de FPS:
    fps.stop()
    print("Tempo de execução: %.2f segundos." %(fps.elapsed()))
    print("Taxa média de quadros por segundo: %.2f FPS." %(fps.fps()))

# Gera um arquivo de log contendo os dados e resultados da execução:
def gerarLog(args, positivo, negativo, fps):
    # Constrói uma lista com os argumentos e seus valores:
    argumentos = [
        ("Diretório de entrada: ", args["entrada"]),
        ("Diretório de saída: ", args["saida"]),
        ("Resultado esperado: ", args["resultado"]),
        ("Diretório do prototexto da rede neural: ", args["prototexto"]),
        ("Diretório do modelo da rede neural: ", args["modelo"]),
        ("Perspectiva do fluxo do tráfego: ", args["perspectiva"]),
        ("Altura dos quadros em pixels: ", args["altura"]),
        ("Largura dos quadros em pixels: ", args["largura"]),
        ("Intervalo de quadros para busca de objetos: ", args["intervalo"]),
        ("Grau de confiança do filtro de detecção: ", args["confianca"]),
        ("Distância euclidiana máxima para convergência de centroides: ",
         (str(args["distancia"]) + " pixels")),
        ("Persistência dos centroides em pós-desaparecimento: ",
         (str(args["desaparecimento"]) + " quadros")),
        ("Métodos de manipulação de imagem utilizados: ", args["manipulacao"]),
    ]

    # Calcula a porcentagem de acertos e desvios do algoritmo:
    if (args["resultado"] is not None):
        try:
            taxa_positivo = ((positivo / args["resultado"][0]) * 100)
        except(ZeroDivisionError):
            taxa_positivo = (positivo * 100)

        try:
            taxa_negativo = ((negativo / args["resultado"][1]) * 100)
        except(ZeroDivisionError):
            taxa_negativo = (negativo * 100)

        taxa_total = (
            ((positivo + negativo) / sum(args["resultado"])) * 100
        )

        try:
            desvio_positivo = abs(
                (positivo - args["resultado"][0]) * (100 / args["resultado"][0])
            )
        except(ZeroDivisionError):
            desvio_positivo = abs(positivo - args["resultado"][0])

        try:
            desvio_negativo = abs(
                (negativo - args["resultado"][1]) * (100 / args["resultado"][1])
            )
        except(ZeroDivisionError):
            desvio_negativo = abs(negativo - args["resultado"][1])

        desvio_total = abs(
            ((positivo + negativo) - sum(args["resultado"]))
            * (100 / sum(args["resultado"]))
        )

    # Gera as strings referentes aos vetores da perspectiva horizontal:
    if (args["perspectiva"] == "horizontal"):
        vetor_positivo = "para a direita"
        vetor_negativo = "para a esquerda"

    # Gera as strings referentes aos vetores da perspectiva vertical:
    elif(args["perspectiva"] == "vertical"):
        vetor_positivo = "subindo"
        vetor_negativo = "descendo"

    # Abre o arquivo de log no diretório especificado, adicionando dados:
    arquivo = open("Logs/" + args["log"] + ".log", "a")

    # Cabeçalho do arquivo de log:
    arquivo.write("..:: PROJETO SEEKER ::.. \n\n")

    # Adiciona os dados sobre os argumentos no arquivo de log:
    for (dado, valor) in argumentos:
        if ((valor is None) or (valor == '')):
            valor = "nenhum"
        arquivo.write(dado + str(valor) + '\n')

    # Adiciona as estatísticas de acerto do algorítmo:
    if ((args["entrada"] is not None) and (args["resultado"] is not None)):
        arquivo.write('\n'
            + ("Quantidade esperada de tráfego %s: %d pessoas;\n"
                %(vetor_positivo, args["resultado"][0])
            )
            + ("Quantidade esperada de tráfego %s: %d pessoas;\n"
                %(vetor_negativo, args["resultado"][1])
            )
            + ("Quantidade esperada de tráfego total: %d pessoas;\n\n"
                %(sum(args["resultado"]))
            )
            + ("Taxa de detecção de pessoas %s: %.2f%% do esperado;\n"
                %(vetor_positivo, taxa_positivo)
            )
            + ("Taxa de detecção de pessoas %s: %.2f%% do esperado;\n"
                %(vetor_negativo, taxa_negativo)
            )
            + ("Taxa de detecção de pessoas no total: %.2f%% do esperado.\n\n"
                %(taxa_total)
            )
            + ("Desvio para as pessoas %s: %.2f%% do esperado;\n"
                %(vetor_positivo, desvio_positivo)
            )
            + ("Desvio para as pessoas %s: %.2f%% do esperado;\n"
                %(vetor_negativo, desvio_negativo)
            )
            + ("Desvio para as pessoas no total: %.2f%% do esperado.\n"
                %(desvio_total)
            )
        )

    # Adiciona as estatísticas finais no arquivo de log:
    arquivo.write('\n'
        + ("Tráfego %s: %d pessoas;\n" %(vetor_positivo, positivo))
        + ("Tráfego %s: %d pessoas;\n" %(vetor_negativo, negativo))
        + ("Pessoas detectadas: %d.\n" %(positivo + negativo))
        + '\n'
        + ("Tempo de execução: %.2f segundos.\n" %(fps.elapsed()))
        + ("Taxa média de quadros por segundo: %.2f FPS.\n" %(fps.fps()))
        + '\n..:: FIM DO LOG ::..\n\n'
    )

    # Encerra o ponteiro de escrita de log:
    arquivo.close()
