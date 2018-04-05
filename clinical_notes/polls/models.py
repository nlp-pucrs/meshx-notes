from django.db import models

class Paciente(models.Model):
	data_paciente = models.CharField(max_length=200)
	tipo = models.TextField(max_length=200)
	resumo_evento = models.TextField(max_length=22)
	registro = models.CharField(max_length=999)
	evento = models.CharField(max_length=999)
	sexo = models.CharField(max_length=1)
	id_paciente = models.CharField(max_length=999)
	gravidade = models.TextField()

	def __str__(self):
		return self.id_paciente