import logging
from typing import List

from django import forms
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column
# from crispy_forms.bootstrap import InlineRadios, Div

from vote.models import (Election, Candidate, VoteBallot, RankBallot, Voter,
    SCORE_MAX, user_is_anonymous, get_or_create_voter)
from vote import voting


class ElectionCreateForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['description', 'etype', 'num_winners', 'num_candidates']


    def clean(self):
        """Make sure num_candidates and num_winners is consistent."""
        cleaned_data = super().clean()
        num_candidates = cleaned_data['num_candidates']
        num_winners = cleaned_data['num_winners']
        if num_winners >= num_candidates:
            raise ValidationError('Number of winners must be less than the number of candidates.')


    def get_num_candidates(self):
        """Get uncleaned number of candidates, before clean and save."""
        cnum = self.data.get('num_candidates', 2)
        return int(cnum)


class CandidateCreateForm00(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CandidateCreateForm00, self).__init__(*args, **kwargs)
        self.fields['name'].required = False

    class Meta:
        model = Candidate
        fields = ['name']

class CandidateCreateForm(forms.Form):
    def __init__(self, num_candidates: int, *args, **kwargs):
        super(CandidateCreateForm, self).__init__(*args, **kwargs)

        self._field_names = self.get_field_names(num_candidates)
        for field_name in self._field_names:
            field = forms.CharField(label='Candidate', max_length=100, )
            self.fields[field_name] = field
            self.fields[field_name].required = False


    def save(self, election: Election):
        for field_name in self._field_names:
            name = self.cleaned_data[field_name]
            candidate = Candidate(name=name, election=election)
            candidate.save()


    @staticmethod
    def get_field_names(num: int):
        """Retrieve the field names for this form. Is a static method."""
        return [f'candidate_{ii}' for ii in range(num)]


    def clean(self):
        """Make candidates are filled in and unique."""
        cleaned_data = super().clean()

        used_candidates = set()
        print('I am the cleaner!')
        for value in cleaned_data.values():
            name = value.strip()
            print('cleaning....', name)
            if len(name) == 0:
                raise ValidationError('Candidate name cannot be empty.')
            if name in used_candidates:
                raise ValidationError('No duplicate candidate names allowed.')
            else:
                used_candidates.add(name)
        return cleaned_data


class VoteForm(forms.Form):
    """Create 1-vote ballot."""

    def __init__(self, candidates : 'QuerySet[Candidate]', *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)

        choices = [(c.pk, c.name) for c in candidates]
        choice = forms.ChoiceField(
            label = 'Your vote',
            choices = choices,
            widget = forms.RadioSelect,
        )
        self.fields['candidate_id'] = choice
        self._candidates = candidates


    def save(self, user: User):
        candidate_id = self.cleaned_data['candidate_id']
        candidate = self._candidates.get(pk=candidate_id)
        election = candidate.election
        voter = get_or_create_voter(election, user)
        v = VoteBallot(vote=True, election=candidate.election, candidate=candidate, voter=voter)
        v.save()
        election.update_voter_num()
        return


def _validate_rank_form_all_zeros(cleaned_data: dict):
    """Make sure ballot is not all zeros!"""
    for value in cleaned_data.values():
        if str(value) != "0":
            return True
    raise ValidationError('At least one candidate must be ranked or rated better than worst.')


class RankForm(forms.Form):
    """Create a ranked ballot"""

    def __init__(self, candidates : 'QuerySet[Candidate]', *args, **kwargs):
        super(RankForm, self).__init__(*args, **kwargs)

        cnum = len(candidates)
        candidate : Candidate
        choice_texts = [str(ii) for ii in range(1, cnum + 1)]
        choice_texts[0] += " (Best)"
        choice_texts[-1] += " (Worst)"

        choice_values = list(range(1, cnum + 1))
        # By votesim convention the worst possible ranking is zero (0) and there can be multiple worst rankings.
        choice_values[-1] = 0

        for candidate in candidates:
            candidate_id  = candidate.pk
            choice = forms.ChoiceField(
                label = candidate.name,
                choices = zip(choice_values, choice_texts),
                widget = forms.RadioSelect(attrs={'class' : 'form-check-input'})
            )
            field_name = 'candidate_' + str(candidate_id)
            self.fields[field_name] = choice

        self._candidates = candidates


    def clean(self):
        """Make sure ranks except for last are not repeating."""
        cleaned_data = super().clean()
        used_ranks = set()
        for key, value in cleaned_data.items():
            if str(value) != "0":
                if value in used_ranks:
                    raise ValidationError('Ranks above "worst" cannot be repeated.')
                else:
                    used_ranks.add(value)
        _validate_rank_form_all_zeros(cleaned_data)
        return cleaned_data


    def save(self, user: User):
        candidates = self._candidates
        election = candidates.first().election
        voter = get_or_create_voter(election, user)

        for candidate in candidates:
            candidate_id  = candidate.pk
            field_name = 'candidate_' + str(candidate_id)
            data = self.cleaned_data[field_name]
            v = RankBallot(vote=data, election=election, candidate=candidate, voter=voter)
            v.save()
        election.update_voter_num()
        return


class ScoreForm(forms.Form):
    def __init__(self, candidates : 'QuerySet[Candidate]', *args, **kwargs):
        super().__init__(*args, **kwargs)

        candidate : Candidate

        choice_values = list(range(0, SCORE_MAX + 1))
        choice_texts = [str(ii) for ii in choice_values]
        choice_texts[0] += " (Worst)"
        choice_texts[-1] += " (Best)"

        for candidate in candidates:
            candidate_id  = candidate.pk
            choice = forms.ChoiceField(
                label = candidate.name,
                choices = zip(choice_values, choice_texts),
                widget = forms.RadioSelect(attrs={'class' : 'form-check-input'})
            )
            field_name = 'candidate_' + str(candidate_id)
            self.fields[field_name] = choice

        self._candidates = candidates


    def save(self, user: User):
        candidates = self._candidates
        election = candidates.first().election

        # Get the voter who is voting.
        try:
            voter  = Voter.objects.get(election=election, user=user)
        except Voter.DoesNotExist:
            voter = Voter(election=election, user=user)
            voter.save()

        for candidate in candidates:
            candidate_id  = candidate.pk
            field_name = 'candidate_' + str(candidate_id)
            data = self.cleaned_data[field_name]
            v = RankBallot(vote=data, election=election, candidate=candidate, voter=voter)
            v.save()
        election.update_voter_num()
        return


    def clean(self):
        cleaned_data = super().clean()
        _validate_rank_form_all_zeros(cleaned_data)
        return cleaned_data


def get_ballot_form(candidates : 'QuerySet[Candidate]', *args, **kwargs):
    """Function to retrieve the right form given a query of candidates."""
    candidate = candidates.first()
    election = candidate.election
    ballot_type = election.ballot_type_str()
    if ballot_type == 'single':
        return VoteForm(candidates, *args, **kwargs)
    elif ballot_type == 'rank':
        return RankForm(candidates, *args, **kwargs)
    elif ballot_type == 'score':
        return ScoreForm(candidates, *args, **kwargs)
    else:
        raise RuntimeError('This should not happen!')




class RecalculateForm(forms.Form):
    def __init__(self, election : Election, *args, **kwargs):
        super(RecalculateForm, self).__init__(*args, **kwargs)
        ballot_type = election.ballot_type
        if ballot_type == voting.ID_SCORE:
            etype_dict = voting.scored_methods
        elif ballot_type == voting.ID_RANK:
            etype_dict = voting.ranked_methods
        elif ballot_type == voting.ID_SINGLE:
            etype_dict = voting.single_methods

        self.etype_dict = etype_dict

        etype = forms.ChoiceField(
            label = 'Recalculate results using different voting method...',
            choices = zip(etype_dict.values(), etype_dict.keys()),
        )
        max_winner = election.num_candidates - 1
        numwinners = forms.IntegerField(
            label = 'New number of winners',
            validators = [MaxValueValidator(max_winner), MinValueValidator(1)],
        )
        self.fields['etype'] = etype
        self.fields['numwinners'] = numwinners

