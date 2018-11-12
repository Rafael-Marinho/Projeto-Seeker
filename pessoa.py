class Pessoa:
	def __init__(self, objID, centroide):
		# Armazena o ID do objeto, inicializa a lista de centroides com o
		# centroide atual e identifica se já foi contabilizado ou não:
		self.objID = objID
		self.centroides = [centroide]
		self.contabilizado = False
