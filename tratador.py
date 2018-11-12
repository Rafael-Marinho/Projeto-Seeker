# -*- coding: utf-8 -*-

import cv2

# Inicializa o estado de subtração de fundo, que deve ser uma constante:
SUBTRACAO = cv2.createBackgroundSubtractorMOG2()

# Função responsável pela manipulação dos quadros, como limiarização e subtração
# de fundo:
def tratar(quadro, tipo):

	# Se houver "bw" em "tipo", a imagem é transformada à escala de cinza:
	if ("bw" in tipo):
		quadro = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY)
		quadro = cv2.cvtColor(quadro, cv2.COLOR_GRAY2BGR)

	# Se houver "threshold" em "tipo", a imagem passa por binarização:
	if ("threshold" in tipo):
		q, quadro = cv2.threshold(quadro, 25, 255, cv2.THRESH_BINARY)

	# Se houver "trunc" em "tipo", a imagem é truncada:
	if ("trunc" in tipo):
		q, quadro = cv2.threshold(quadro, 82, 255, cv2.THRESH_TRUNC)

	# Se houver "zero" em "tipo", realiza um "truncamento inverso":
	if ("zero" in tipo):
		q, quadro = cv2.threshold(quadro, 42, 255, cv2.THRESH_TOZERO)

	# Se houver "realce" em "tipo", são realçadas as bordas idetificadas:
	if ("realce" in tipo):
		mascara =cv2.bitwise_not(cv2.Canny(quadro, 255, 255, 1))
		quadro = cv2.bitwise_and(quadro, quadro, mask = mascara)

	# Se houver "borda" em "tipo", o vídeo é reduzido às bordas identificadas:
	elif ("borda" in tipo):
		quadro = cv2.Canny(quadro, 192, 64, 1)
		quadro = cv2.cvtColor(quadro, cv2.COLOR_GRAY2BGR)

	# Se houver "sub" em "tipo", o vídeo passa por subtração de fundo:
	if ("sub" in tipo):
		quadro = SUBTRACAO.apply(quadro)
		quadro = cv2.cvtColor(quadro, cv2.COLOR_GRAY2BGR)

	return (quadro)

# Teste:
from imutils.video import VideoStream
def teste():
	# source = VideoStream(src=0).start()
	source = cv2.VideoCapture(0)
	while (1 < 2):
		quadro = source.read()[1]
		cv2.imshow("Projeto Seeker", tratar(quadro, "bw zero"))
		esc = (cv2.waitKey(1) & 0xFF)
		if (esc == ord("q")):
			break
# teste()
