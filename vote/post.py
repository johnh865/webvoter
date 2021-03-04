from itertools import cycle
import logging
import textwrap
import numpy as np
import votesim
from vote import voting
from vote.models import Election, Candidate, SCORE_MAX

from bokeh.plotting import figure
from bokeh.palettes import RdYlBu

from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
import markdown

logger = logging.getLogger(__name__)

class PostElection:
    """
    Parameters
    ----------
    election_id : int
        Election data pk
    method : str or None
        Election Method type to postprocess data. Set to None to use the method specified for election.
    """

    def __init__(self, election_id : int, etype: str=None, numwinners: int=None):
        self.election = Election.objects.get(pk=election_id)
        if etype is None or etype == '':
            etype = self.election.etype
            method_name = self.election.method_str()
        else:
            method_name = voting.all_methods_inv[etype]

        self.etype = etype
        self.data, self.candidate_ids, self.voter_num = self._get_data()
        self.candidate_names = [Candidate.objects.get(pk=ii).name for ii in self.candidate_ids]
        self.candidate_names = np.array(self.candidate_names)
        self.method_name = method_name

        self.scoremax = self._get_tally_maxscore()


        if numwinners is None:
            numwinners = self.election.num_winners
        self.numwinners = numwinners

        self.erunner = votesim.votemethods.eRunner(etype=etype, numwinners=numwinners, ballots=self.data)
        logging.debug(self.erunner.output)
        winner_indices  = self.erunner.winners_no_ties
        logging.debug('Winners indices = %s', winner_indices)
        tie_indices = self.erunner.ties
        logger.debug('tie_indices=%s', tie_indices)
        tie_indices = np.array(tie_indices, dtype=int)

        self.winners = self.candidate_names[winner_indices]
        self.ties = self.candidate_names[tie_indices]


    def _get_tally_maxscore(self):
        if self.election.ballot_type == voting.ID_SINGLE:
            scoremax= 1
        else:
            scoremax = SCORE_MAX
        return scoremax


    def write_text_winner(self):
        """Write some text on who won and who lost."""
        if len(self.winners) == 0:
            text = ' <b>No winners found.</b> '
        else:
            if len(self.winners) == 1:
                text = 'Winner is: '
            else:
                text = 'Winners are: '
            text += '<b>' + ', '.join(self.winners) + '</b>'
        return text


    def write_text_ties(self):

        if len(self.ties) > 0:
            text = ' * Tied choices: '
            text += ', '.join(self.ties)
        else:
            text = ''
        return text

    def output_markdown(self):
        s = ''
        for key, value in self.erunner.output.items():
            s += f'{key} = \n{value}\n\n'
        s = s.replace('\n', '\n   ')
        return markdown.markdown(s)




    def _get_data(self):
        """Get candidate data and candidate id's."""
        election = self.election
        # Get the candidates
        candidates = election.candidate_set.all()
        candidate_ids = [c.id for c in candidates]
        candidate_num = len(candidate_ids)
        candidate_ids_index = np.arange(candidate_num)

        search_dict = dict(zip(candidate_ids, candidate_ids_index))

        def get_candidate_index(id):
            """Retrieve candidate array index."""
            return search_dict[id]

        # Get all votes
        ballots = election.get_ballots()
        ballots_voter_ids = [b.voter.id for b in ballots]
        ballots_candidate_ids = [b.candidate.id for b in ballots]
        ballots_votes = [b.vote for b in ballots]

        # Turn into numpy arrays
        ballots_voter_ids = np.asarray(ballots_voter_ids)
        ballots_candidate_ids = np.asarray(ballots_candidate_ids)
        ballots_votes = np.asarray(ballots_votes)

        # Get unique voters
        ballots_voter_ids_unique, inv_index = np.unique(ballots_voter_ids, return_inverse=True)

        candidate_id_index = [get_candidate_index(ii) for ii in ballots_candidate_ids]
        candidate_id_index = np.asarray(candidate_id_index)

        voter_num = len(ballots_voter_ids_unique)
        data = np.zeros((voter_num, candidate_num))
        data[inv_index, candidate_id_index] = ballots_votes

        return data, candidate_ids, voter_num


    def get_plots(self):
        etype = self.etype
        logger.debug('Getting etype = %s', etype)

        if etype == votesim.votemethods.PLURALITY:
            return [self.plot_tally()]

        elif etype == votesim.votemethods.SCORE:
            return [self.plot_score()]

        elif (etype == votesim.votemethods.IRV or
              etype == votesim.votemethods.IRV_STV or
              etype == votesim.votemethods.STV_GREGORY):
            return [self.plot_irv()]

        elif etype == votesim.votemethods.STAR:
             return [self.plot_score(), self.plot_runoff_star()]

        elif etype == votesim.votemethods.TOP_TWO:
            return [self.plot_tally(), self.plot_runoff()]

        elif (etype == votesim.votemethods.RANKED_PAIRS or
              etype == votesim.votemethods.SMITH_MINIMAX  ):
            return [self.plot_margin_matrix()]

        elif etype == votesim.votemethods.BORDA:
            return [self.plot_score()]

        elif etype == votesim.votemethods.SMITH_SCORE:
            return [self.plot_margin_matrix()]

        else:
            logger.warning('Method %s has no plotting', etype)
            return []





    def plot_tally(self):
        """Plot tally, for FPTP, approval, score methods."""
        names = self.candidate_names
        output = self.erunner.output
        try:
            tally = output['first_tally']
        except KeyError:
            tally = output['tally']

        title = 'Ballot Tally'
        return self.plot_runoff_html(names, tally, title=title)



    def plot_score(self):
        """Plot tally, for FPTP, approval, score methods."""
        names = self.candidate_names
        output = self.erunner.output
        try:
            tally = output['first_tally']
        except KeyError:
            tally = output['tally']

        title = 'Ballot Average Score'
        tally = tally / self.voter_num
        return self.plot_score_html(names, tally, title=title)


    def plot_runoff(self):
        output = self.erunner.output
        candidate_indices = output['runoff_candidates']
        tally = output['runoff_tally']
        names = self.candidate_names[candidate_indices]
        title = 'Runoff Tally'
        return self.plot_runoff_html(names, tally, title=title)


    def plot_runoff_star(self):
        output = self.erunner.output
        matrix = output['runoff_matrix']
        candidate_indices = output['runoff_candidates']

        vm = votesim.votemethods.condcalcs.VoteMatrix(matrix=matrix)
        tally = vm.worst_votes

        title = 'STAR Runoff Tally'
        names = self.candidate_names[candidate_indices]
        return self.plot_runoff_html(names, tally, title=title)



    def plot_irv(self, title='Accumulated Votes for Each Round'):
        names = self.candidate_names
        output = self.erunner.output
        voter_num = self.voter_num
        logger.debug('IRV data')
        logger.debug(self.data)
        logger.debug('IRV data shape = %s', self.data.shape)
        logger.debug('IRV output')
        logger.debug(output)
        history = output['round_history']
        left = np.zeros(len(history[0]))
        # colors = cycle(['lightblue', 'orangered', 'palegreen',])
        colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
        colors = cycle(colors)

        plot = figure(
            y_range = names,
            plot_height=500,
            plot_width=800,
            title=title,
            tools='save',
            tooltips = [
                ('candidate', '@names'),
                ('net votes', '@right'),
                ('round', '@round'),
            ]
        )

        for ii, votes in enumerate(history):
            delta = votes - left
            delta = np.maximum(0, delta)
            right = left + delta
            vote_percent = right / voter_num * 100

            labels = []
            round = []
            for ileft, idelta, vp in zip(left, delta, vote_percent):
                if idelta ==0 or np.isnan(idelta):
                    labels.append('')
                    round.append('')
                else:
                    labels.append(f'  R{ii+1} - {vp:2.1f}%')
                    round.append(ii+1)

            data = dict(names=names, left=left, right=right, labels=labels, round=round)
            data = ColumnDataSource(data=data)
            plot.hbar(
                y = 'names',
                left = 'left',
                right = 'right',
                source = data,
                height = 0.5,
                fill_color = next(colors),
            )
            left = right

            plot.text(
                source=data, y='names', x='left',
                text='labels',
                text_align='left',
                text_baseline='middle',
                text_font_size='12px',
            )

        plot.xaxis.axis_label_text_font_size = '12pt'
        plot.xaxis.major_label_text_font_size = '12pt'
        plot.yaxis.axis_label_text_font_size = '12pt'
        plot.yaxis.major_label_text_font_size = '12pt'
        plot.xaxis.axis_label = 'Net Votes For Each Round R'

        html = file_html(plot, CDN, title=title)
        return html


    def plot_margin_matrix(self):
        names = self.candidate_names
        output = self.erunner.output
        matrix = output['vote_matrix']
        return self.plot_margin_matrix_html(names, matrix, title='Head-to-Head Vote Margins')


    def plot_margin_matrix_html(self, names, vote_matrix, width=800, title=''):
        candidates1, candidates2 = np.meshgrid(names, names)
        max_name_len = max(len(c) for c in names)
        vote_matrix = np.asarray(vote_matrix)
        voter_num  = self.voter_num
        margins = (vote_matrix - vote_matrix.T) / voter_num * 100
        height = len(names) * 90 + max_name_len * 5

        votes_for = np.ravel(vote_matrix)
        votes_against = np.ravel(vote_matrix.T)
        candidates2 = candidates2.ravel()
        candidates1 = candidates1.ravel()


        margins = margins.ravel()
        # texts = ['{0:+0.0f}%'.format(t) for t in margins]
        texts = []
        for c2, c1, margin in zip(candidates2, candidates1, margins):
            if c1 == c2:
                texts.append('-')
            else:
                texts.append(f'{margin:+0.0f}%')

        data = dict(
            candidate=candidates2,
            against_candidate=candidates1,
            margins=margins,
            votes_for=votes_for,
            votes_against=votes_against,
            texts = texts,
            )

        # Some colors from bokeh docs
        # colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
        # colors.reverse()
        # mapper = LinearColorMapper(palette=colors, low=margins.min(), high=margins.max())
        mapper = LinearColorMapper(palette=RdYlBu[11], low=50, high=-50)
        print(data)
        plot = figure(
            y_range = names,
            x_range = names,
            plot_height=height,
            plot_width=width,
            title=title,
            tools='save',
            tooltips = [
                ('candidate', '@candidate'),
                ('against', '@against_candidate'),
                ('votes for', '@votes_for'),
                ('votes against', '@votes_against'),
            ]
        )
        plot.rect(
            source=data, y='candidate', x='against_candidate', width=1, height=1,
            fill_color={'field': 'margins', 'transform': mapper},
            line_color="#111111",
            )

        plot.text(
            source=data, y='candidate', x='against_candidate',
            text='texts',
            text_align='center',
            text_baseline='middle',
            text_font_size='18px',
        )
        plot.xaxis.axis_label_text_font_size = '12pt'
        plot.xaxis.major_label_text_font_size = '12pt'
        plot.xaxis.major_label_orientation = np.pi / 2
        plot.xaxis.axis_label = '...Against Candidate'

        plot.yaxis.axis_label_text_font_size = '12pt'
        plot.yaxis.major_label_text_font_size = '12pt'
        plot.yaxis.axis_label = 'Candidate Vote Margin...'
        html = file_html(plot, CDN, title=title)
        return html


    def plot_score_html(self, names, tally, width=800, title='', ):
        """Write html for tally plot."""
        scoremax = self.scoremax
        rating = tally / scoremax * 100
        texts = []
        height = len(names) * 60 + 60

        for t, r in zip(tally, rating):
            texts.append(f'  {r:0.1f}% ({t:0.2f} / {scoremax:0.0f})  ')

        data = dict(candidate=names, tally=tally, rating=rating, texts=texts)
        data = ColumnDataSource(data=data)
        plot = figure(
            y_range = names,
            plot_height=height,
            plot_width=width,
            title=title,
            tools='save',
            tooltips = [
                ('candidate', '@candidate'),
                ('rating %', '@rating'),
                ('average score', '@tally'),
            ]
        )
        plot.hbar(
            y = 'candidate',
            right = 'rating',
            source = data,
            height=0.75,
            )
        plot.text(
            source=data,
            y='candidate',
            x = 'rating',
            text='texts',
            text_align='right',
            text_baseline='middle',
            text_font_size='12px',
            color = '#FFFFFF'
        )
        plot.xaxis.axis_label_text_font_size = '12pt'
        plot.xaxis.major_label_text_font_size = '12pt'
        plot.yaxis.axis_label_text_font_size = '12pt'
        plot.yaxis.major_label_text_font_size = '12pt'

        html = file_html(plot, CDN, title=title)
        return html


    def plot_runoff_html(self, names, tally, width=800, title='', ):
        """Write html for runoff tally plot."""
        net_votes = np.sum(tally)
        height = len(names) * 60 + 60
        
        rating = tally  / net_votes * 100
        texts = []
        for t, r in zip(tally, rating):
            texts.append(f'  {r:0.1f}% ({t:0.0f} Votes)  ')

        data = dict(candidate=names, tally=tally, rating=rating, texts=texts)
        data = ColumnDataSource(data=data)
        plot = figure(
            y_range = names,
            plot_height=height,
            plot_width=width,
            title=title,
            tools='save',
            tooltips = [
                ('candidate', '@candidate'),
                ('votes %', '@rating'),
                ('# of votes', '@tally'),
            ]
        )
        plot.hbar(
            y = 'candidate',
            right = 'rating',
            source = data,
            height=0.75,
            )
        plot.text(
            source=data,
            y='candidate',
            x = 'rating',
            text='texts',
            text_align='right',
            text_baseline='middle',
            text_font_size='12px',
            color = '#FFFFFF'
        )
        plot.xaxis.axis_label_text_font_size = '12pt'
        plot.xaxis.major_label_text_font_size = '12pt'
        plot.yaxis.axis_label_text_font_size = '12pt'
        plot.yaxis.major_label_text_font_size = '12pt'

        html = file_html(plot, CDN, title=title)
        return html
