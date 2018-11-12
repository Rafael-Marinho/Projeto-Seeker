# -*- coding: utf-8 -*-

import collections
import numpy as np
from scipy.spatial import distance as dist

class Centroide:
	def __init__(self, desap=50, distancia=50):
		# Inicializa o identificador do objeto único em dois dicionários
		# ordenados, afim de mapeá-lo quadro-a-quadro e identificar quantas
		# vezes ele foi marcado como "desaparecido":
		self.objID = 0
		self.objetos = collections.OrderedDict()
		self.desaparecido = collections.OrderedDict()

		# Variáveis responsáveis: pelo armazenamento do número máximo de quadros
		# consecutivos até um objeto ser marcado como "desaparecido" e deixar de
		# ser rastreado (desap); distância euclidiana máxima entre os centroides:
		self.desap = desap

		# Armazena o máximo valor entre dois centroides para determiná-los como
		# um único objeto:
		self.distancia = distancia
		# (Se a distância for maior que tal valor, o mesmo é denominado
		# "desaparecido")

	# Registra o centroide do objeto no posterior ID disponível:
	def registrar(self, centroide):
		self.objetos[self.objID] = centroide
		self.desaparecido[self.objID] = 0
		self.objID += 1

	# Remove o ID do objeto dos dicionários de registro:
	def desregistrar(self, objID):
		del self.objetos[objID]
		del self.desaparecido[objID]

	# Checa se a lista de delimitadores está vazia:
	def atualizar(self, delimit):
		if (len(delimit) == 0):

			# Procura se há algum objeto rastreado e o marca como desaparecido:
			for id in list(self.desaparecido.keys()):
				self.desaparecido[id] += 1

				# Se o objeto atingiu o limite de quadros como "desaparecido", o
				# mesmo é apagado do registro:
				if self.desaparecido[id] > self.desap:
					self.desregistrar(id)

			# Assim que for atestada a ausência de centroides ou informações de
			# rastreio a serem atualizadas, a função dá seu retorno:
			return (self.objetos)

		# Inicializa um array com os centroides entrados no quadro atual:
		centroidesAtuais = np.zeros((len(delimit), 2), dtype="int")

		# Faz uma varredura nos retângulos delimitados e os usa suas coordenadas
		# para derivar os mesmos:
		for (cen, (xInicial, yInicial, xFinal, yFinal)) in enumerate(delimit):
			cX = int((xInicial + xFinal) / 2.0)
			cY = int((yInicial + yFinal) / 2.0)
			centroidesAtuais[cen] = (cX, cY)

		# Registra o centroide de entrada quando não estiver rastreando objetos:
		if (len(self.objetos) == 0):
			for cen in range(0, len(centroidesAtuais)):
				self.registrar(centroidesAtuais[cen])

		# Analiza os centroides de entrada em relação aos objetos já existentes:
		else:
			# Captura os IDs e seus respectivos centroides:
			IDs = list(self.objetos.keys())
			objCentroides = list(self.objetos.values())

			# Calcula a distância euclidiana entre os centroides registrados e os
			# centroides de entrada, afim de corrigir falsos-positivos:
			D = dist.cdist(np.array(objCentroides), centroidesAtuais)

			# Identifica o menor valor em cada linha e coluna de D e organiza as
			# mesmas na ordem crescente das linhas, afim de colocar os menores
			# valores na frente:
			linhas = D.min(axis=1).argsort()
			colunas = D.argmin(axis=1)[linhas]

			# Declara conjuntos com os IDs dos objetos já examinados, afim de
			# determinar quais devem ser atualizados, registrados ou excluídos:
			linhasUsadas = set()
			colunasUsadas = set()

			# Examina a matriz de centroides afim de identificar novos objetos:
			for (linha, coluna) in zip(linhas, colunas):
				# Condição que ignora as linhas e colunas já examinadas:
				if ((linha in linhasUsadas) or (coluna in colunasUsadas)):
					continue

				# Condição que ignora os objetos com centroides cujas distâncias
				# euclidianas são maiores que o limite para considerará-las como
				# um único objeto, assim mantendo-as como objetos separados:
				if D[linha, coluna] > self.distancia:
					continue

				# Pega o ID da linha atual e a define como seu novo centroide,
				# reiniciando o contador de desaparecidos. Ao fim, após examinar
				# todas as linha e colunas, as adicionam às listas de ignorancia
				# (linhasUsadas e colunasUsadas):
				objID = IDs[linha]
				self.objetos[objID] = centroidesAtuais[coluna]
				self.desaparecido[objID] = 0
				linhasUsadas.add(linha)
				colunasUsadas.add(coluna)

			# Arrays que armazenam as linhas e colunas ainda não examinadas:
			linhasLivres = set(range(0, D.shape[0])).difference(linhasUsadas)
			colunasLivres = set(range(0, D.shape[1])).difference(colunasUsadas)

			# No caso do número de objetos ser maior ou igual à quantidade de
			# centroides de entrada, é investigado o desaparecimento de objetos:
			if (D.shape[0] >= D.shape[1]):
				# Examina os endereços remanescentes, pega o ID do objeto
				# correspondente e incrementa o contador de desaparecidos:
				for linha in linhasLivres:
					id = IDs[linha]
					self.desaparecido[id] += 1

					# Checa se a quantidade de quadros em que o objeto foi
					# taxado como "desaparecido" excede o limite de
					# desaparecimento:
					if (self.desaparecido[id] > self.desap):
						self.desregistrar(id)

			# Se os centroides excedentes não desapareceram de fato, eles são
			# registrados como novos objetos:
			else:
				for coluna in colunasLivres:
					self.registrar(centroidesAtuais[coluna])

		# Retorna o conjunto de objetos rastreáveis:
		return (self.objetos)
