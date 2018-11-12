# -*- coding: utf-8 -*-

# Importação dos pacotes e módulos externos:
from pessoa import Pessoa
from centroide import Centroide
from tratador import tratar
from analisador import analisar
from analisador import gerarLog

import argparse
import time

import numpy as np
import dlib
import cv2
from imutils import resize
from imutils.video import VideoStream
from imutils.video import FPS


# Construtor dos argumentos:
ap = argparse.ArgumentParser()
ap.add_argument(
	"-e", "--entrada", type=str,
	help="Diretório da entrada de vídeo (deixe em branco para webcam)"
)
ap.add_argument(
	"-s", "--saida", type=str,
	help="Diretório do da saída de vídeo (deixe em branco para não gravar)"
)
ap.add_argument("-r", "--resultado", nargs=2, type=int,
	help="Tupla contendo o resultado esperado (vetor positivo, vetor negativo)"
)
ap.add_argument(
	"-a", "--manipulacao", type=str, default='',
	help="Métodos de manipulação de imagem a serem utilizadas"
)
ap.add_argument(
	"-t", "--prototexto", type=str,
	default="Modelos/MobileNetSSD_deploy.prototxt",
	help="Diretório do prototexto da rede neural profunda convolucional do SSD"
)
ap.add_argument(
	"-m", "--modelo", type=str,
	default="Modelos/MobileNetSSD_deploy.caffemodel",
	help="Diretorio do modelo da rede neural profunda convolucional do SSD"
)
ap.add_argument(
	"-p", "--perspectiva", type=str, default="horizontal",
	help="Define a perspectiva 'horizontal ou 'vertical' (padrão=horizontal)"
)
ap.add_argument(
	"-H", "--altura", type=int, default=500,
	help="Altura em pixels dos quadros do vídeo (padrão=680)"
)
ap.add_argument(
	"-w", "--largura", type=int, default=500,
	help="Largura em pixels dos quadros do video (padrão=500)"
)
ap.add_argument(
	"-c", "--confianca", type=float, default=0.4,
	help="Probabilidade mínima para filtrar problemas de detecção (padrão=0.4)"
)
ap.add_argument(
	"-i", "--intervalo", type=int, default=30,
	help="Quantidade de quadros entre uma detecção em outra (padrão=30)"
)
ap.add_argument(
	"-f", "--desaparecimento", type=int, default=30,
	help="Quantidade máxima de quadros da persistência de centroides ao deixar de ser rastreado (padrão=30)"
)
ap.add_argument(
	"-d", "--distancia", type=int, default=150,
	help="Máxima distância euclidiana para definir dois ou mais centroides como um único centroide (padrão=150)"
)
ap.add_argument("-l", "--log", type=str, help="Diretório do arquivo de log")
args = vars(ap.parse_args())

# Constante que inicializa as classe importadas pelo modelo pré-treinado
# mobileNet SSD Caffe, é o que o algorítmo está preparado para identificar:
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

# Carrega o modelo pré-treinado:
print("Carregando o modelo...")
dnn = cv2.dnn.readNetFromCaffe(args["prototexto"], args["modelo"])

# Define uma captura de imagem pela webcam na ausência do argumento de entrada:
if (not args.get("entrada", False)):
	print("Iniciando captura pela webcam...")
	source = VideoStream(src=0).start()

# Define o vídeo do argumento de entrada como o vídeo a ser analizado:
else:
	print("Acessando o arquivo de vídeo...")
	source = cv2.VideoCapture("Testes/" + args["entrada"])

# Inicializa as constantes responsáveis pelas dimensões do quadro em píxels (H
# para a altura e W para largura), bem como a variável de escrita (usada no caso
# de um argumento para arquivo de saída), a lista de rastreadores, um dicionário
# para os IDs dos objetos rastreáveis e instancia o rastreador de centroides:
H = None
W = None
escritor = None
rastreadores = []
rastreaveis = {}
cent = Centroide(desap=args["desaparecimento"], distancia=args["distancia"])

# Inicia suas variáveis referentes ao vetor do objeto na imagem:
positivo = 0
negativo = 0

# Nomeia os vetores para o caso de perspectiva horizontal:
if (args["perspectiva"] == "horizontal"):
	vetor_positivo = "Direita"
	vetor_negativo = "Esquerda"

# Nomeia os vetores para o caso de perspectiva vertical:
elif(args["perspectiva"] == "vertical"):
	vetor_positivo = "Subindo"
	vetor_negativo = "Descendo"

# Inicia as variáveis responsáveis pela contagem de quadros e a taxa de FPS:
quadros = 0
fps = FPS().start()

# Faz uma varredura nos quadros do vídeo:
while (1 < 2):
	quadro = source.read()

	# Lê o quadro atual e identifica se trata-se de uma gravação ou uma captura:
	if (args.get("entrada", False)):
		quadro = quadro[1]

	# Identifica se atingiu o fim do vídeo, na eventualidade do quadro ser nulo:
	if ((quadro is None) and (args["entrada"] is not None)):
		break

	# Trata o quadro de acordo com os argumentos passados:
	if (args["manipulacao"] != ''):
		try:
			quadro = tratar(quadro, args["manipulacao"])
		except(cv2.error):
			None

	# Redimensiona o quadro (afim de agilizar e facilitar o processamento) de
	# acordo com a perspectiva (altura para vertical e largura para horizontal)
	# e o converte de BRG para RGB afim de ser trabalhado pela biblioteca DLIB:
	if (args["perspectiva"] == "horizontal"):
		quadro = resize(quadro, width=args["largura"])
	elif (args["perspectiva"] == "vertical"):
		quadro = resize(quadro, height=args["altura"])
	rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)

	# Define as dimensões (altura e largura) do quadro:
	if ((W is None) or (H is None)):
		(H, W) = quadro.shape[:2]

	# Inicializa o escritor, para o caso de haver um argumento de saída:
	if ((escritor is None) and (args["saida"] is not None)):
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		escritor = cv2.VideoWriter(
			"Gravados/" + args["saida"], fourcc, 30, (W, H), True
		)

	# Define o estado inicial junto e inicia a lista de caixas de limites
	# (retângulos que definem objetos) do detector de objetos e de correlações:
	estado = "Procurando"
	caixas = []

	# A cada determinado número de quadros, a rede neural busca detectar novos
	# objetos (operação mais cara computacionalmente que o rastreio):
	if ((quadros % args["intervalo"]) == 0):
		# Na detecção, define o estado e inicializa o conjunto de rastreadores:
		estado = "Detectando"
		rastreadores = []

		# Converte o quadro em um BLOB e o passa pela rede neural afim de
		# detectar objetos:
		blob = cv2.dnn.blobFromImage(quadro, 0.007843, (W, H), 127.5)
		dnn.setInput(blob)
		deteccoes = dnn.forward()

		# Examina as detecções:
		for i in np.arange(0, deteccoes.shape[2]):
			# Extrai o grau de confiança (probabilidade) associado à previsão:
			confianca = deteccoes[0, 0, i, 2]

			# Filtra falsos-positivos pelo critério do mínimo grau de confiança:
			if (confianca > args["confianca"]):
				# Extrai o índice da lista de classes na lista de detecções:
				indice = int(deteccoes[0, 0, i, 1])

				# Ignora caso o objeto identificado não for uma pessoa:
				if (CLASSES[indice] != "person"):
					continue

				# Calcula as cordenadas da caixa do objeto, as constrói com a
				# biblioteca DLIB e assim inicia o rastreador de correlações,
				# então adicionando-o à lista de rastreadores:
				caixa = (deteccoes[0, 0, i, 3:7] * np.array([W, H, W, H]))
				(xInicial, yInicial, xFinal, yFinal) = caixa.astype("int")
				rastreador = dlib.correlation_tracker()
				retangulo = dlib.rectangle(xInicial, yInicial, xFinal, yFinal)
				rastreador.start_track(rgb, retangulo)
				rastreadores.append(rastreador)

	# Nos demais quadros, usa rastreadores ao invés de detectores, apresentando
	# também melhor fluxo de quadros:
	else:
		# Examina a lista de rastreadores:
		for rastreador in rastreadores:
			# Define o estado como "rastreando" e atualiza o rastreador,
			# capturando sua nova posição e guardando-a em variáveis que geram
			# uma tupla então adicionada na lista de caixas:
			estado = "Rastreando"
			rastreador.update(rgb)
			posicao = rastreador.get_position()
			xInicial = int(posicao.left())
			yInicial = int(posicao.top())
			xFinal = int(posicao.right())
			yFinal = int(posicao.bottom())
			caixas.append((xInicial, yInicial, xFinal, yFinal))

	# Desenha uma linha vertical, demarcando o limiar da inferência:
	if (args["perspectiva"] == "horizontal"):
		cv2.line(quadro, (W // 2, H), (W // 2, 0), (255, 255, 0), 1)

	# Desenha uma linha horizontal, demarcando o limiar da inferência:
	elif(args["perspectiva"] == "vertical"):
		cv2.line(quadro, (0, H // 2), (W, H // 2), (255, 255, 0), 1)

	# Usa o rastreador de centroide para associar os centroides de objetos
	# antigos com os mais recentes:
	objetos = cent.atualizar(caixas)

	# Faz uma varredura sobre os objetos rastreados:
	for (id, centroid) in objetos.items():
		# Identifica se um objeto rastreável existe para o ID atual:
		rastreado = rastreaveis.get(id, None)

		# Na ausência de um objeto rastreável, cria um:
		if (rastreado is None):
			rastreado = Pessoa(id, centroid)

		# Determina a posição do objeto rastreado:
		else:
			# A diferença entre as coordenadas do objeto atual e a distância
			# euclidiana deve dizer qual a direção de movimento do objeto:
			if (args["perspectiva"] == "horizontal"):
				x = [c[0] for c in rastreado.centroides]
				direcao = (centroid[1] - np.mean(x))

			elif(args["perspectiva"] == "vertical"):
				y = [c[1] for c in rastreado.centroides]
				direcao = (centroid[1] - np.mean(y))

			# Insere então o centroide na lista de rastreados:
			rastreado.centroides.append(centroid)

			# Motor de inferência:
			if (rastreado.contabilizado == False):
				if (args["perspectiva"] == "horizontal"):
					# Se a direção for negativa (indicando movimento para
					# direita) e o centroide está à direita do limiar, conta o
					# objeto:
					if ((direcao < 0) and (centroid[0] < (W // 2))):
						positivo += 1
						rastreado.contabilizado = True

					# Se a direção for positiva (indicando movimento para
					# esqueda), e o centroide está a esqueda do limiar, conta o
					# objeto:
					elif ((direcao > 0) and (centroid[0] > (W // 2))):
						negativo += 1
						rastreado.contabilizado = True

				elif(args["perspectiva"] == "vertical"):
					# Se a direção for negativa (indicando movimento para cima)
					# e o centroide está à direita do limiar, conta o objeto:
					if ((direcao < 0) and (centroid[1] < (H // 2))):
						positivo += 1
						rastreado.contabilizado = True

					# Se a direção for positiva (indicando movimento para
					# baixo), e o centroide está a esqueda do limiar, conta o
					# objeto:
					elif ((direcao > 0) and (centroid[1] > (H // 2))):
						negativo += 1
						rastreado.contabilizado = True

		# Armazena o ID do objeto na lista de objetos rastreados:
		rastreaveis[id] = rastreado

		# Insere um rótulo para cada objeto identificado no quadro, evidenciando
		# a posição do centroide e ID:
		cv2.putText(quadro, ("ID " + str(id)),
			((centroid[0]), (centroid[1] - 12)), cv2.FONT_HERSHEY_SIMPLEX,
			0.3, (0, 255, 0), 1
		)
		cv2.putText(quadro, "+", (centroid[0], centroid[1]),
			cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1
		)

	# Constrói uma lista com informações que devem ser dispostas no quadro:
	informacoes = [
		(vetor_positivo, positivo),
		(vetor_negativo, negativo),
		("Estado", estado),
	]

	# Dispõe as informações no canto do quadro:
	for (i, (dado, valor)) in enumerate(informacoes):
		cv2.putText(quadro, (dado + ": " + str(valor)), (10, ((i * 15) + 20)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1
		)

	# Identifica se o vídeo deve ser gravado no diretório do argumento:
	if (escritor is not None):
		escritor.write(quadro)

	# Mostra o quadro na tela:
	cv2.imshow("Projeto Seeker", quadro)
	esc = (cv2.waitKey(1) & 0xFF)

	# Se a tecla "Q" for pressionada, o loop é quebrado:
	if (esc == ord("q")):
		break

	# Incrementa quantidade de quadros processados e atualiza o contador de FPS:
	quadros += 1
	fps.update()

# Se o vídeo foi gravado, o ponteiro do escritor é liberado:
if (escritor is not None):
	escritor.release()

# Se tratando de uma gravação pela webcam, interrompe a gravação:
if (not args.get("entrada", False)):
	source.stop()

# Se foi acessado um arquivo, o ponteiro de leitura é liberado:
else:
	source.release()

# Encerra e fecha qualquer janela aberta:
cv2.destroyAllWindows()

# Gera um dump referente aos resultados da execução:
analisar(args["perspectiva"], positivo, negativo, fps)

# Gera um arquivo de log contendo os dados e resultados da execução:
if (args["log"] is not None):
	gerarLog(args, positivo, negativo, fps)
