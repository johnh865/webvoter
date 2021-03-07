"""Create fake user election data."""
import numpy as np
from vote import models
from vote import voting
import votesim
from votesim.models import spatial
from django.core.management.base import BaseCommand

def get_user_bots(num:int):
    """Create or get user bots."""
    users = []
    for ii in range(num):
        username = f'Bot-{ii:03d}'
        user = models.get_or_create_user(username)
        users.append(user)
    return users


def gen_irv_data():
    """
    correct_history = [[42, 26, 15, 17],
                    [42, 26,  0, 32],
                    [42,  0,  0, 58]]
    """
    d = [[1, 2, 3, 4]]*42 + \
        [[4, 1, 2, 3]]*26 + \
        [[4, 3, 1, 2]]*15 + \
        [[4, 3, 2, 1]]*17
    ballot_data = np.array(d)

    name = voting.NAME_IRV
    etype = voting.get_method_id(name)
    e1 = models.Election(etype=etype, ballot_type=voting.ID_RANK, description='test irv: Favorite Book?', num_candidates=4)
    e1.save()
    c1 = models.Candidate(name='Game of Thrones', election=e1)
    c2 = models.Candidate(name='Hunger Games', election=e1)
    c3 = models.Candidate(name='Crime and Punishment', election=e1)
    c4 = models.Candidate(name='To Kill a Mockingbird', election=e1)
    candidates = [c1, c2, c3, c4]
    [c.save() for c in candidates]

    rank_ballots = []
    voters = []
    for ii, ballot in enumerate(ballot_data):
        username = f'Bot-{ii:03d}'
        user = models.get_or_create_user(username)
        voter = models.Voter(election=e1, user=user)
        voter.save()
        voters.append(voter)
    # models.Voter.objects.bulk_create(voters)

    for ii, ballot in enumerate(ballot_data):
        for rank, candidate in zip(ballot, candidates):
            rank_ballot = models.RankBallot(vote=rank, voter=voters[ii], election=e1, candidate=candidate)
            # rank_ballots.append(rank_ballot)
            rank_ballot.save()

    # models.RankBallot.objects.bulk_create(rank_ballots)
    return


def gen_irv_data2():
    # Generate randomized voter ballot data
    numvoters = 100
    num_candidates = 5
    v = spatial.Voters(seed=0,)
    v.add_random(numvoters=numvoters, ndim=2, )
    c = spatial.Candidates(voters=v, seed=0)
    c.add_random(cnum=num_candidates, sdev=1.0)
    e = spatial.Election(voters=v, candidates=c)
    ballot_data, _ = e.ballotgen.get_ballots(
        etype=votesim.votemethods.IRV,
        strategies=(),
    )

    name = voting.NAME_IRV
    etype = voting.get_method_id(name)
    e1 = models.Election(etype=etype, ballot_type=voting.ID_RANK, description='test irv: Favorite Fruit?', num_candidates=num_candidates)
    e1.save()
    c1 = models.Candidate(name='Apples', election=e1)
    c2 = models.Candidate(name='Bananas', election=e1)
    c3 = models.Candidate(name='Cranberries', election=e1)
    c4 = models.Candidate(name='Jelly Donuts', election=e1)
    c5 = models.Candidate(name='Tomatoes', election=e1)
    candidates = [c1, c2, c3, c4, c5]
    [c.save() for c in candidates]

    # Generate voters
    users = get_user_bots(numvoters)
    voters = []
    for user in users:
        voter = models.Voter(election=e1, user=user)
        voter.save()
        voters.append(voter)

    # Generate ballots
    for ii, ballot in enumerate(ballot_data):
        for rank, candidate in zip(ballot, candidates):
            rank_ballot = models.RankBallot(vote=rank, voter=voters[ii], election=e1, candidate=candidate)
            rank_ballot.save()
    return


def gen_score_data():
    # Generate randomized voter ballot data
    numvoters = 99
    num_candidates = 5
    v = spatial.Voters(seed=400,)
    v.add_random(numvoters=numvoters, ndim=2, )
    c = spatial.Candidates(voters=v, seed=0)
    c.add_random(cnum=num_candidates, sdev=1.0)
    e = spatial.Election(voters=v, candidates=c)
    ballot_data, _ = e.ballotgen.get_ballots(
        etype=votesim.votemethods.SCORE,
        strategies=(),
    )

    name = voting.NAME_SCORE
    etype = voting.get_method_id(name)
    e1 = models.Election(etype=etype, ballot_type=voting.ID_RANK, description='test score: Favorite City?', num_candidates=num_candidates)
    e1.save()
    c1 = models.Candidate(name='Tokyo', election=e1)
    c2 = models.Candidate(name='New York', election=e1)
    c3 = models.Candidate(name='Houston', election=e1)
    c4 = models.Candidate(name='Baghdad', election=e1)
    c5 = models.Candidate(name='Sao Paulo', election=e1)
    candidates = [c1, c2, c3, c4, c5]
    [c.save() for c in candidates]

    # Generate voters
    users = get_user_bots(numvoters)
    voters = []
    for user in users:
        voter = models.Voter(election=e1, user=user)
        voter.save()
        voters.append(voter)

    # Generate ballots
    for ii, ballot in enumerate(ballot_data):
        for rank, candidate in zip(ballot, candidates):
            rank_ballot = models.RankBallot(vote=rank, voter=voters[ii], election=e1, candidate=candidate)
            rank_ballot.save()


def build():
    elections = models.Election.objects.filter(description='test score: Favorite City?').all()
    if len(elections) > 0:
        return
    else:
        gen_irv_data()
        gen_irv_data2()
        gen_score_data()

    models.Election.update_all()
    return


class Command(BaseCommand):
    help = 'Create fake election data with bots'

    def handle(self, *args, **kwargs):
        build()



if __name__ == '__main__':
    build()