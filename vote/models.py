from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

import numpy as np
from vote import voting


# Create your models here.

# Method names and ID's from the voting module
METHOD_NAMES = voting.all_method_names
METHOD_IDS = voting.all_method_ids

METHOD_TYPES =  voting.METHOD_TYPES
METHOD_TYPE_IDS = voting.METHOD_TYPE_IDS

# Some voting application settings
CANDIDATE_NUM_MAX = 30
WINNER_NUM_MAX = CANDIDATE_NUM_MAX - 1
SCORE_MAX = 5

# Default user name
USER_ANONYMOUS = 'anonymous'

def get_default_user():
    """Retrieve default anonymous user."""
    return  get_user_model().objects.get_or_create(username=USER_ANONYMOUS)[0]


def get_or_create_user(name:str):
    """Retrieve or create a user."""
    return  get_user_model().objects.get_or_create(username=name)[0]


class Election(models.Model):
    """Basic election storage container."""
    id = models.AutoField(primary_key=True)
    etype = models.CharField(
        'Election method',
        choices = zip(METHOD_IDS, METHOD_NAMES),
        max_length=20,
        )
    ballot_type = models.SmallIntegerField(
        'Ballot type',
        choices = zip(METHOD_TYPE_IDS, METHOD_TYPES)
        )
    num_winners = models.PositiveSmallIntegerField(
        '# of winners',
        validators = [MaxValueValidator(WINNER_NUM_MAX), MinValueValidator(1)],
        # choices = zip(WINNER_RANGE, WINNER_RANGE),
        default = 1,
        )
    num_candidates = models.PositiveSmallIntegerField(
        '# of candidates',
        # choices = zip(CANDIDATE_RANGE, CANDIDATE_RANGE),
        validators = [MaxValueValidator(CANDIDATE_NUM_MAX), MinValueValidator(1)],
        default = 2,
        )

    description = models.CharField('Poll question', max_length=200)
    date_published = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.ballot_type = voting.get_ballot_type_id(self.etype)
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.id) + '. ' + self.description


    def ballot_type_str(self):
        """Get ballot type"""
        return METHOD_TYPES[self.ballot_type]


    def method_str(self):
        """Get election method used."""
        return voting.all_methods_inv[self.etype]


    def get_etype(self):
        return self.etype


    def get_ballot_set(self):
        if self.ballot_type == voting.ID_SINGLE:
            return self.voteballot_set
        else:
            return self.rankballot_set


    def voter_num(self):
        """get number of voters found for election."""
        ballots = self.get_ballot_set().all()
        ballots_voter_ids = [b.voter.id for b in ballots]
        return len(np.unique(ballots_voter_ids))


    # def user_ballots(self, user):
    #     """get all ballots a user has cast in this election."""
    #     ballots = self.get_ballots().



    def candidate_names(self):
        """Get names of all candidates."""
        candidates = self.candidate_set.all()
        names = [c.name for c in candidates]
        return names


    def get_ballots(self):
        """Get all ballot cast in election."""
        if self.ballot_type == voting.ID_SINGLE:
            return self.voteballot_set.all()
        else:
            return self.rankballot_set.all()




class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Candidate', max_length=100)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)


    def __str__(self):
        return 'Elect.' + str(self.election.id) + '-' + self.name


class Voter(models.Model):

    id = models.AutoField(primary_key=True)
    # ip = models.GenericIPAddressField()
    # email = models.EmailField()

    user = models.ForeignKey(
        User,
        on_delete = models.SET(get_default_user)
        )

    election = models.ForeignKey(Election, on_delete=models.CASCADE)


    def __str__(self):
        if self.user.username == USER_ANONYMOUS:
            return 'Elec.' + str(self.election.id) + '-' + self.user.username + '-' + str(self.id)
        return 'Elec.' + str(self.election.id) + '-' + self.user.username


class VoteBallot(models.Model):
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    vote = models.BooleanField('Candidate vote marking',)


    def __str__(self):
        return str(self.candidate.name) + '-' + str(self.voter.user.username)


class RankBallot(models.Model):
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    vote = models.IntegerField('Candidate ranking')


    def __str__(self):
        return str(self.election) + '-' + str(self.candidate.name) + '-' + str(self.voter.user.username)