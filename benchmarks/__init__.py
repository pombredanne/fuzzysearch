from fuzzysearch.levenshtein import \
    find_near_matches_levenshtein_linear_programming
from fuzzysearch.levenshtein_ngram import \
    find_near_matches_levenshtein_ngrams as fnm_levenshtein_ngrams
from fuzzysearch.substitutions_only import \
    find_near_matches_substitutions_ngrams as fnm_substitutions_ngrams, \
    find_near_matches_substitutions_linear_programming
from fuzzysearch.generic_search import \
    find_near_matches_generic_linear_programming
import pyximport
pyximport.install()
from fuzzysearch._generic_search import \
    find_near_matches_generic_linear_programming as \
    find_near_matches_generic_linear_programming_cython
import random


def fnm_levenshtein_lp(subsequence, sequence, max_l_dist):
    return list(find_near_matches_levenshtein_linear_programming(
        subsequence, sequence, max_l_dist))

def fnm_substitutions_lp(subsequence, sequence, max_substitutions):
    return list(find_near_matches_substitutions_linear_programming(
        subsequence, sequence, max_substitutions))

def fnm_generic_lp(subsequence, sequence, max_l_dist):
    return list(find_near_matches_generic_linear_programming(
        subsequence, sequence, max_l_dist, max_l_dist, max_l_dist, max_l_dist))

def fnm_generic_lp_cython(subsequence, sequence, max_l_dist):
    return list(find_near_matches_generic_linear_programming_cython(
        subsequence, sequence, max_l_dist, max_l_dist, max_l_dist, max_l_dist))


search_functions = {
    'levenshtein_lp': fnm_levenshtein_lp,
    'levenshtein_ngrams': fnm_levenshtein_ngrams,
    'substitutions_lp': fnm_substitutions_lp,
    'substitutions_ngrams': fnm_substitutions_ngrams,
    'generic_lp': fnm_generic_lp,
    'generic_lp_cython': fnm_generic_lp_cython,
}

benchmarks = {
    'dna_no_match': dict(
        subsequence = 'GCTAGCTAGCTA',
        sequence = "ATCG" * (10**3),
        max_dist = 1,
    ),
    'dna_no_match2': dict(
        subsequence = 'ATGATGATG',
        sequence = 'ATCG' * (10**3),
        max_dist = 2,
    ),
    'random_kevin': dict(
        subsequence = ''.join(random.choice('ATCG') for _i in xrange(36)),
        sequence = ''.join(random.choice('ATCG' * 5 + 'N') for _i in xrange(90)),
        max_dist = 3,
    ),
    'random_kevin_partial_match': dict(
        subsequence = 'AAGTCTAGT' + ''.join(random.choice('ATCG') for _i in xrange(36-9)),
        sequence = 'AAGTCTAGT' + ''.join(random.choice('ATCG' * 5 + 'N') for _i in xrange(90-9)),
        max_dist = 3,
    ),
}


def get_benchmark(search_func_name, benchmark_name):
    search_func = search_functions[search_func_name]
    search_args = dict(benchmarks[benchmark_name])

    if search_func in (fnm_levenshtein_ngrams, fnm_levenshtein_lp, fnm_generic_lp, fnm_generic_lp_cython):
        search_args['max_l_dist'] = search_args.pop('max_dist')
    elif search_func in (fnm_substitutions_ngrams, fnm_substitutions_lp):
        search_args['max_substitutions'] = search_args.pop('max_dist')
    else:
        raise Exception('Unsupported search function: %r' % search_func)

    return search_func, search_args


def run_benchmark(search_func, search_args):
    return search_func(**search_args)
