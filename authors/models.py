from django.db import models

# Create your models here.
class Author(models.Model):
    def __str__(self):
        return f'{self.name}'

    name = models.CharField(max_length=80, unique=True)
    