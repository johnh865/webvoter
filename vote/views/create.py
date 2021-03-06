import pdb
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from vote import voting

from vote.models import Candidate, Election, get_default_user
from vote.forms import ElectionCreateForm, CandidateCreateForm, VoteForm, CandidateCreateForm00
from vote.views.latest import ElectionListView
# Create your views here.

ELECTION_FORM_NAME = 'form_data'
CANDIDATE_FORM_NAME = 'candidate_form_data'
ELECTION_IDS_COOKIE = 'election_ids'

ELECTION_INIT_DEFAULT = {
    'num_candidates':2,
}

logger = logging.getLogger(__name__)


class CreateElectionView(View):
    election_list_view = ElectionListView()


    def get_elections(self):
        """Get latest elections from ElectionListView."""
        return self.election_list_view.get_queryset()


    def get(self, request, *args, **kwargs):
        e_init = request.session.get(ELECTION_FORM_NAME, ELECTION_INIT_DEFAULT)

        e_form = ElectionCreateForm(initial=e_init)
        cnum = e_form.get_num_candidates()

        c_init = request.session.get(CANDIDATE_FORM_NAME, {})
        c_form = CandidateCreateForm(cnum, initial=c_init)

        context = {
            'e_form' : e_form,
            'c_form' : c_form,
            'elections' : self.get_elections()}

        return render(request, 'vote/create.html', context)


    def post(self, request, *args, **kwargs):
        e_form = ElectionCreateForm(request.POST)
        cnum = e_form.get_num_candidates()

        if 'candidate_update' in request.POST:
            messages.success(request, f'Number of Candidates has been updated to {cnum}')
            c_form = CandidateCreateForm(cnum, initial=request.POST)

        elif 'submit' in request.POST:
            c_form = CandidateCreateForm(cnum, request.POST)

            if e_form.is_valid() and c_form.is_valid():

                election = e_form.save()
                c_form.save(election)

                etype = e_form.cleaned_data.get('etype')
                method = voting.all_methods_inv[etype]

                messages.success(request, f'You have successfully created a {method} election.')
                return redirect('create-ballot', election_id=election.pk)

            else:
                messages.error(request, 'Invalid form submission.')

                for key, value in e_form.errors.items():
                    messages.error(request, key + ' - ' + str(value))

                for key, value in c_form.errors.items():
                    messages.error(request, key + ' - ' + str(value))

        context = {
            'e_form' : e_form,
            'c_form' : c_form,
            'elections' : self.get_elections()}

        # Save form data to temporarily to session
        request.session[ELECTION_FORM_NAME] = e_form.data
        request.session[CANDIDATE_FORM_NAME] = c_form.data

        return render(request, 'vote/create.html', context)



# def create_election(request):
#     """Create an election"""
#     if request.method == 'POST':
#         e_form = ElectionCreateForm(request.POST)
#         request.session[ELECTION_FORM_NAME] = e_form.data

#         c_handler = CandidateHandler(request)
#         c_forms = c_handler.forms

#         if 'submit' in request.POST and e_form.is_valid():
#             election = c_handler.save()

#             etype = e_form.cleaned_data.get('etype')
#             method = voting.all_methods_inv[etype]
#             messages.success(request, f'You have successfully created a {method} election.')
#             return redirect('create-ballot', election_id=election.pk)

#         elif 'candidate_update' in request.POST:
#             context = {'e_form' : e_form, 'c_forms' : c_forms}
#             cnum = request.session[ELECTION_FORM_NAME]['num_candidates']
#             messages.success(request, f'# of Candidates has been updated to {cnum}')
#             return render(request, 'vote/create.html', context)

#     else:
#         if ELECTION_FORM_NAME in request.session:
#             e_form = ElectionCreateForm(initial=request.session[ELECTION_FORM_NAME])
#         else:
#             e_form = ElectionCreateForm(initial=e_init)

#         c_handler = CandidateHandler(request)
#         c_forms = c_handler.forms

#         context = {'e_form' : e_form, 'c_forms' : c_forms}
#         return render(request, 'vote/create.html', context)

class _NOT_USED___CandidateHandler:
    """Handle retrieving candidate name data & creating Candidate forms.
    Forms are created at initialization. """
    def __init__(self, request):

        e_form = ElectionCreateForm(request.POST)
        cnum = e_form.data.get('num_candidates', 2)
        self.cnum = int(cnum)
        self.request = request
        self.e_form = e_form

        logger.debug('loading candidate forms')
        self.form = self._load_form(request)
        return


    def _load_form(self, request):
        init = request.session.get(CANDIDATE_FORM_NAME, {})
        c_form = CandidateCreateForm(self.cnum, initial=init)
        return c_form


    def save_session_data(self):
        """Save election form data to the session"""
        self.request.session[ELECTION_FORM_NAME] = self.e_form.data
        self.request.session[CANDIDATE_FORM_NAME] = self.form.data


    def save(self):
        """Save to database"""
        election = self.e_form.save()
        self.form.save(election)

        # clear out the session data.
        self.request.session.pop(ELECTION_FORM_NAME)
        self.request.session.pop(CANDIDATE_FORM_NAME)
        return election

class _NOT_USED___CandidateHandler00:
    """Handle retrieving candidate name data & creating Candidate forms.
    Forms are created at initialization. """
    def __init__(self, request):

        e_form = ElectionCreateForm(request.POST)
        cnum = e_form.data.get('num_candidates', 2)
        self.cnum = int(cnum)
        self.request = request
        self.e_form = e_form
        self.forms = self._load_forms()
        return

    def _load_forms(self):
        session_candidate_data = self.load_session_candidates()
        c_forms = []
        if session_candidate_data:
            for ii in range(self.cnum):
                try:
                    c_name = session_candidate_data[ii]
                    c_form_i = CandidateCreateForm00(initial={'name' : c_name})
                except IndexError:
                    c_form_i = CandidateCreateForm00()
                c_forms.append(c_form_i)
            return c_forms
        else:
            return self._create_new_forms()


    def load_session_candidates(self) -> list:
        # Even though candidates from separate form, we must query the ELECTION_FORM_NAME
        # to get the data from request.POST, which is stored in a QueryDict.
        try:
            d = self.request.session[ELECTION_FORM_NAME]
            return d.getlist('name', [])
        except (KeyError, AttributeError):
            return []


    def load_form_candidates(self) -> list:
        try:
            d = self.e_form.data
            return d.getlist('name', [])
        except (KeyError, AttributeError):
            return []


    def save_session_data(self):
        """Save election form data to the session"""
        self.request.session[ELECTION_FORM_NAME] = self.e_form.data


    def _create_new_forms(self):
        c_forms = []
        for _ in range(self.cnum):
            c_form_i = CandidateCreateForm0()
            c_forms.append(c_form_i)
        return c_forms


    def save(self):
        """Save to database"""
        election = self.e_form.save()
        candidates = self.load_form_candidates()
        for candidate in candidates:
            c = Candidate(name=candidate, election=election)
            c.save()

        # clear out the session data.
        self.request.session.pop(ELECTION_FORM_NAME)
        return election
