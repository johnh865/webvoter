import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View

from vote import voting

from vote.models import Candidate, Election, get_default_user
from vote.forms import ElectionCreateForm, CandidateCreateForm, VoteForm, get_ballot_form
# Create your views here.

ELECTION_IDS_COOKIE = 'election_ids'

e_init = {
    'num_candidates':2,
}

BALLOT_FORM_NAME = 'ballot_form_data'
logger = logging.getLogger(__name__)
class UserHandler:
    def __init__(self, request):
        self.request = request
        self.is_authenticated = request.user.is_authenticated

        if request.user.is_authenticated:
            self.user = request.user
        else:
            self.user = get_default_user()


def user_has_voted(request, election_id: int):
    """bool : Determine whether the current user in current session has voted yet."""
    user_handler = UserHandler(request)
    user = user_handler.user
    election = get_object_or_404(Election, pk=election_id)

    if user_handler.is_authenticated:
        voters = user.voter_set.filter(election=election)
        if len(voters) > 0:
            voteballots = voters[0].voteballot_set.all()
            if len(voteballots) > 0:
                return True
            rankballots = voters[0].rankballot_set.all()
            if len(rankballots) > 0:
                return True

    # Check if anonymous voter has voted
    else:
        election_ids = request.COOKIES.get(ELECTION_IDS_COOKIE)

        # Search in anonymous user's cookies for an election id.
        if election_ids:
            election_ids = election_ids.split(',')
            if str(election_id) in election_ids:
               return True
    return False


def get_ballot_template(election: Election) -> str:
    """Get html template for the ballot type."""
    ballot_type = election.ballot_type
    if ballot_type == voting.ID_RANK:
        template = 'vote/rank.html'
    elif ballot_type == voting.ID_SCORE:
        template = 'vote/rank.html'
    elif ballot_type == voting.ID_SINGLE:
        template = 'vote/vote.html'
    return template

class CreateBallotView(View):

    def _init_request(self, request, election_id: int):

        election = get_object_or_404(Election, pk=election_id)
        candidates = election.candidate_set.all()
        user_handler = UserHandler(request)
        user = user_handler.user

        # Check if registered user has voted
        has_voted = user_has_voted(request, election_id)

        self.election = election
        self.candidates = candidates
        self.user = user
        self.user_handler = user_handler
        self.has_voted = has_voted
        self.request = request
        self.election_id =  election_id


    def _has_voted(self):
        """Handle user that has already voted."""
        messages.error(self.request, f"You ({self.user.username}) already voted!")
        return redirect('view-results', self.election_id)


    def _render_ballot(self, request):
        """Render the ballot."""

        init_data = request.session.get(BALLOT_FORM_NAME, {})
        context = {'form' : get_ballot_form(self.candidates, initial=init_data) }
        template = get_ballot_template(self.election)
        return render(request, template, context)


    def get(self, request, election_id: int):
        self._init_request(request, election_id)
        if self.has_voted:
            return self._has_voted()

        return self._render_ballot(request)


    def post(self, request, election_id: int):
        self._init_request(request, election_id)
        if self.has_voted:
            return self._has_voted()

        candidates = self.candidates
        form = get_ballot_form(candidates, request.POST)
        if form.is_valid():
            return self._post_valid_form(form)
        else:
            return self._post_invalid_form(form)


    def _post_valid_form(self, form: VoteForm):
        form.save(self.user)
        request = self.request
        election_id = self.election_id
        user = self.user

        # Delete session ballot data
        if BALLOT_FORM_NAME in request.session:
            del request.session[BALLOT_FORM_NAME]

        messages.success(request, f'Vote submitted for "{user.username}"!')
        response = redirect('view-results', election_id)

        # Set a cookie for anonymous voters
        if not self.user_handler.is_authenticated:
            messages.success(request, "Setting a cookie")

            try:
                election_ids = request.COOKIES[ELECTION_IDS_COOKIE]
            except KeyError:
                election_ids = ''

            election_ids += f',{election_id}'
            response.set_cookie(ELECTION_IDS_COOKIE, election_ids)
        return response


    def _post_invalid_form(self, form: VoteForm):
        request = self.request

        messages.error(request, 'Invalid form submission.')
        for key, value in form.errors.items():
            messages.error(request, key + ' - ' + str(value))

        # Save invalid form data to session.
        request.session[BALLOT_FORM_NAME] = form.data
        logger.debug('the invalid data is...')
        logger.debug(form.data)
        return self._render_ballot(request)


# def create_ballot(request, election_id: int):
#     """create a ballot"""
#     election = get_object_or_404(Election, pk=election_id)
#     candidates = election.candidate_set.all()
#     user_handler = UserHandler(request)
#     user = user_handler.user

#     # Check if registered user has voted
#     has_voted = user_has_voted(request, election_id)

#     # Make sure people who have already voted are redirected.
#     if has_voted:
#         messages.error(request, f"You ({user.username}) already voted!")
#         return redirect('view-results', election_id)

#     # Post the vote form.
#     if request.method == 'POST':
#         form = get_ballot_form(candidates, request.POST)
#         # candidate_id = form.cleaned_data.get('candidate_id')
#         if form.is_valid():
#             form.save(user)

#             # Delete session ballot data
#             del request.session[BALLOT_FORM_NAME]

#             messages.success(request, f'Vote submitted for "{user.username}"!')
#             response = redirect('view-results', election_id)

#             # Set a cookie for anonymous voters
#             if not user_handler.is_authenticated:
#                 messages.success(request, "Setting a cookie")
#                 try:
#                     election_ids = request.COOKIES[ELECTION_IDS_COOKIE]
#                 except KeyError:
#                     election_ids = ''
#                 election_ids += f',{election_id}'
#                 response.set_cookie(ELECTION_IDS_COOKIE, election_ids)
#             return response
#         else:
#             messages.error(request, 'Invalid form submission.')
#             for key, value in form.errors.items():
#                 messages.error(request, key + ' - ' + str(value))

#             # Save invalid form data to session.
#             request.session[BALLOT_FORM_NAME] = form.data

#             return redirect('create-ballot', election_id=election.pk)

#     # Render ballot if user has not yet voted.
#     if not has_voted:
#         context = {'form' : get_ballot_form(candidates) }
#         template = get_ballot_template(election)
#         return render(request, template, context)

