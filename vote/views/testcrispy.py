

import pdb

import numpy as np
import votesim
import markdown

from bokeh.plotting import figure
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from vote import voting
from vote.forms import ExampleForm


def test_crispy(request):
    form = ExampleForm()
    context = {'form' : form }
    return render(request, 'vote/rank.html', context=context)
