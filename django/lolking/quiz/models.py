from django.db import models
from jsonfield import JSONField

# Create your models here.
class Quiz(models.Model):
    qid = models.AutoField(primary_key=True)
    which = models.IntegerField(default=-1)
    question = models.CharField(max_length=1023, default='', blank=True)
    answer = models.CharField(max_length=31, default='', blank=True)
    pic = models.CharField(max_length=1023, default='', blank=True)
    ans_list = JSONField(default=[])

    def answerme(self, i_choice):
        try:
            self.answer = self.ans_list[i_choice]
            self.which = i_choice
            return self.answer
        except Exception as e:
            return '(null)'

