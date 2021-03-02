
from django.test import TestCase
import numpy as np

from vote import models
from vote import voting

# Create your tests here.


class Test1(TestCase):
    def test_get_default_user(self):
        user = models.get_default_user()
        print(user)
        self.assertTrue(user.username == 'anonymous')


    def test_create_voter(self):
        election = models.Election(method=1, description='test election')
        v = models.Voter(election=election)
        


class TestIRV(TestCase):
    def test_wiki(self):

        d = [[1, 2, 3, 4]]*42 + \
            [[4, 1, 2, 3]]*26 + \
            [[4, 3, 1, 2]]*15 + \
            [[4, 3, 2, 1]]*17
        ballot_data = np.array(d)

        method = voting.NAME_IRV
        method_id = voting.get_method_id(method)

        e1 = models.Election(method=method_id, ballot_type=voting.ID_RANK, description='test irv')
        e1.save()
        c1 = models.Candidate(name='a', election=e1)
        c2 = models.Candidate(name='b', election=e1)
        c3 = models.Candidate(name='c', election=e1)
        c4 = models.Candidate(name='d', election=e1)
        candidates = [c1, c2, c3, c4]
        [c.save() for c in candidates]
        for ii, ballot in enumerate(ballot_data):
            username = f'Bot-{ii}'
            user = models.get_or_create_user(username)
            voter = models.Voter(election=e1, user=user)
            voter.save()
            user.save()

            for rank, candidate in zip(ballot, candidates):
                rank_ballot = models.RankBallot(vote=rank, voter=voter, election=e1, candidate=candidate)
                rank_ballot.save()

        