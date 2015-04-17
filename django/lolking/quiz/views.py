from django.shortcuts import render
from django.http import HttpResponse
from quiz.models import Quiz
from rest_framework.renderers import JSONRenderer

# Create your views here.
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def get_answer(request):
    d_get = request.GET
    if 'qid' in d_get:
        try:
            mo_quiz = Quiz.objects.get(pk=d_get['qid'])
            return HttpResponse(mo_quiz.answer)
        except (Quiz.DoesNotExist) as e:
            return HttpResponse('no this question')
    elif 'kw' in d_get:
        a_res = []
        a_quiz = Quiz.objects.filter(question__contains=d_get['kw'])
        for it_quiz in a_quiz:
            a_res.append({'question':it_quiz.question, 'answer':it_quiz.answer})
        return JSONResponse(a_res)
    return HttpResponse('need qid or kw')

