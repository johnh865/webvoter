import pdb

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from vote import voting

from vote.models import Candidate, Election, get_default_user
from vote.forms import ElectionCreateForm, CandidateCreateForm, VoteForm, get_ballot_form
# Create your views here.

ELECTION_IDS_COOKIE = 'election_ids'

e_init = {
    'num_candidates':2,
}



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
    ballot_type = election.ballot_type_str()
    if ballot_type == 'rank':
        template = 'vote/rank.html'
    elif ballot_type == 'score':
        template = 'vote/rank.html'
    elif ballot_type == 'vote':
        template = 'vote/vote.html'
    return template


def create_ballot(request, election_id: int):
    """create a ballot"""
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidate_set.all()
    user_handler = UserHandler(request)
    user = user_handler.user

    # Check if registered user has voted
    has_voted = user_has_voted(request, election_id)

    # Make sure people who have already voted are redirected.
    if has_voted:
        messages.error(request, f"You ({user.username}) already voted!")
        return redirect('view-results', election_id)

    # Post the vote form.
    if request.method == 'POST':
        form = get_ballot_form(candidates, request.POST)
        # candidate_id = form.cleaned_data.get('candidate_id')
        if form.is_valid():
            form.save(user)
            messages.success(request, f'Vote submitted for "{user.username}"!')

            response = redirect('view-results', election_id)

            # Set a cookie for anonymous voters
            if not user_handler.is_authenticated:
                messages.success(request, "Setting a cookie")
                try:
                    election_ids = request.COOKIES[ELECTION_IDS_COOKIE]
                except KeyError:
                    election_ids = ''
                election_ids += f',{election_id}'
                response.set_cookie(ELECTION_IDS_COOKIE, election_ids)
            return response
        else:
            messages.error(request, 'Invalid form submission.')
            return redirect('create-ballot', election_id=election.pk)

    # Render ballot if user has not yet voted.
    if not has_voted:
        context = {'form' : get_ballot_form(candidates) }
        template = get_ballot_template(election)
        return render(request, template, context)

