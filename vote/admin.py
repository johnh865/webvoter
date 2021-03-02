from django.contrib import admin
from vote.models import Election, Candidate, Voter, VoteBallot, RankBallot

admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Voter)
admin.site.register(VoteBallot)
admin.site.register(RankBallot)

# Register your models here.
