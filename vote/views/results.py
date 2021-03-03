
import pdb

import numpy as np
import votesim
import markdown
from vote.forms import RecalculateForm


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.views import View

from vote import voting

from vote.models import Candidate, Election, get_default_user
from vote.post import PostElection
from vote.views.ballot import user_has_voted

# def view_results(request, election_id, etype=None):
#     post = PostElection(election_id=election_id, etype=etype)
#     plots = post.get_plots()
#     # markdown = post.markdown

#     context = {
#         'post' : post,
#         'bokeh_plots' : plots,
#         'output' : post.output_markdown
#     }
#     return render(request, 'vote/results.html', context=context)


class ResultsView(View):

    def get(self, request, election_id, etype=None, numwinners=None, *args, **kwargs):
        post = PostElection(election_id=election_id, etype=etype, numwinners=numwinners)
        plots = post.get_plots()
        form = RecalculateForm(
            post.election,
            initial={'etype' : post.etype, 'numwinners' : post.numwinners}
        )
        # markdown = post.markdown

        context = {
            'post' : post,
            'bokeh_plots' : plots,
            'output' : post.output_markdown,
            'form' : form,
        }
        return render(request, 'vote/results.html', context=context)


    def post(self, request, election_id, *args, **kwargs):
        election = Election.objects.get(pk=election_id)
        form = RecalculateForm(election, data=request.POST)

        if 'submit' in request.POST and form.is_valid():
            etype = form.cleaned_data['etype']
            numwinners = form.cleaned_data['numwinners']
            kwargs['etype'] = etype
            kwargs['numwinners'] = numwinners
            return redirect('view-results-etype-numwinners', election_id=election_id, *args, **kwargs)

        elif 'vote' in request.POST:
            # kwargs['etype'] = election.get_etype()
            return redirect('create-ballot', election_id=election_id)


