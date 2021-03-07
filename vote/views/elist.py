
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from vote import voting
from vote.models import Candidate, Election, get_default_user


from django.views.generic import ListView, DetailView

class ElectionListLatestView(ListView):
    model = Election
    template_name = 'vote/latest.html'
    context_object_name = 'elections'
    ordering = ['-date_published']
    paginate_by = 10


class ElectionListPopularView(ListView):
    model = Election
    template_name = 'vote/latest.html'
    context_object_name = 'elections'
    ordering = ['-num_voters']
    paginate_by = 10

