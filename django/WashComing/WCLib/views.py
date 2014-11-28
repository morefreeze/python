# coding=utf-8
from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.template import loader, Context
import xml.etree.ElementTree as ET
import math

# Create your views here.
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

EPS = 1e-7
def eq_zero(f_val):
    return math.fabs(f_val) < EPS

def etree_to_dict(t):
    d = {t.tag : map(etree_to_dict, list(t))}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['_text'] = t.text
    return d
