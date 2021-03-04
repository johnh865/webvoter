"""Get election method data from votesim.
"""

import votesim
from votesim import votemethods

METHOD_TYPES = ('single', 'score', 'rank', 'approval' )
ID_SINGLE = 0
ID_SCORE = 1
ID_RANK = 2
ID_APPROVAL = 3
METHOD_TYPE_IDS = [ID_SINGLE, ID_SCORE, ID_RANK, ID_APPROVAL]

# Names of all voting methods
NAME_IRV  = 'Instant Runoff'
NAME_STV_HARE = 'Single Transferable Vote // Hare'
NAME_SRV_GREG = 'Single Transferable Vote // Gregory'
NAME_RANKED_PAIRS = 'Ranked Pairs'
NAME_SMITH_MINIMAX = 'Smith//Minimax'
NAME_BORDA = 'Borda'
NAME_TOP_TWO = 'Top Two Automatic Runoff'
NAME_COPELAND = 'Copeland'
NAME_BLACK = 'Black'

NAME_SCORE = 'Score'
NAME_STAR = 'STAR (Score then Automatic Runoff)'
NAME_SMITH_SCORE = 'Smith//Score'
NAME_MAJ_JUDGE = 'Majority Judgment'
NAME_RRW = 'Reweighted Range'
NAME_SEQ_MONROE = 'Sequential Monroe'

NAME_FPTP = 'First Past the Post'

# Categorization of voting methods and corresponding str keys in votesim module.
ranked_methods = {
    NAME_IRV : votemethods.IRV,
    NAME_STV_HARE : votemethods.IRV_STV,
    NAME_SRV_GREG : votemethods.STV_GREGORY,
    NAME_RANKED_PAIRS : votemethods.RANKED_PAIRS,
    NAME_SMITH_MINIMAX : votemethods.SMITH_MINIMAX,
    NAME_BORDA : votemethods.BORDA,
    NAME_TOP_TWO : votemethods.TOP_TWO,
    NAME_COPELAND : votemethods.COPELAND,
    NAME_BLACK : votemethods.BLACK,
}
scored_methods = {
    NAME_SCORE : votemethods.SCORE,
    NAME_STAR: votemethods.STAR,
    NAME_SMITH_SCORE : votemethods.SMITH_SCORE,
    NAME_MAJ_JUDGE : votemethods.MAJORITY_JUDGMENT,
    NAME_RRW : votemethods.REWEIGHTED_RANGE,
    NAME_SEQ_MONROE : votemethods.SEQUENTIAL_MONROE,
}

single_methods = {NAME_FPTP : votemethods.PLURALITY}
all_methods = single_methods.copy()
all_methods.update(ranked_methods)
all_methods.update(scored_methods)

# Get method name from keyname.
all_methods_inv = {v:k for k, v in all_methods.items()}


# List[str] of all method names
all_method_names = list(all_methods.keys())

# List[int] of all method ID's
all_method_ids = list(all_methods.values())
# all_method_ids = list(range(len(all_method_names)))
# all_method_id_dict = dict(zip(all_method_names, all_method_ids))

# List[func] of all method functions
all_method_etype_list = list(all_methods.values())


def get_method_id(method : str):
    """Given method name, retrieve method ID."""
    return all_methods[method]



def _get_ballot_type_str(method : str):
    """Get type of ballot for voting method. Returns 'score', 'rank', or 'single'."""
    if method in single_methods:
        return ID_SINGLE
    elif method in scored_methods:
        return ID_SCORE
    elif method in ranked_methods:
        return ID_RANK



def _get_ballot_type_id(etype : str) -> int:
    """Get int id of ballot given integer id of voting method. Return 0, 1, or 2"""
    if etype in single_methods.values():
        return ID_SINGLE
    elif etype in scored_methods.values():
        return ID_SCORE
    elif etype in ranked_methods.values():
        return ID_RANK


_get_method_type_id_dict = {k : _get_ballot_type_id(k) for k in all_method_ids}


def get_ballot_type_id(etype : str) -> int:
    """Get int id of ballot given integer id of voting method. Return 0, 1, or 2"""
    return _get_method_type_id_dict[etype]


# List[str] = method types
all_method_types = [_get_ballot_type_str(m) for m in all_method_names]

# List[int] = method ballot type id's
all_method_type_ids = [_get_ballot_type_id(m) for m in all_method_ids]


