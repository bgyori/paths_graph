import random
import unittest
import networkx as nx
from paths_graph import PathsGraph
from paths_graph.path_checker import PathChecker, HypothesisTester
from paths_graph.path_checker.ltl_nodes import build_tree 


def test_parse_formula_atomic():
    formula = '[5]'
    tree = build_tree(formula)
    formula = '![5]'
    tree = build_tree(formula)
    formula = '[5]|[4]'
    tree = build_tree(formula)
    formula = '[5] | [4]'
    tree = build_tree(formula)


def test_parse_formula_future_global():
    formula = 'F([5])'
    tree = build_tree(formula)
    formula = 'G(![5])'
    tree = build_tree(formula)


def _run_cases(test_cases):
    for formula, nodes, tf_expected in test_cases:
        pc = PathChecker(formula, nodes)
        assert pc.truth == tf_expected, \
            'Got unexpected %s for %s with nodes %s' % (pc.truth, formula,
                                                        str(nodes))


def test_path_checker_batch_atomic():
    test_cases = [('[5]', ['5'], True),
                  ('[5]', ['4'], False),
                  ('[5]', ['5', '4'], True),
                  ('[5]', ['4', '5'], False)]
    _run_cases(test_cases)


def test_path_checker_batch_atomic_neg():
    test_cases = [('![5]', ['5'], False),
                  ('![5]', ['4'], True),
                  ('![5]', ['5', '4'], False),
                  ('![5]', ['4', '5'], True)]
    _run_cases(test_cases)


def test_path_checker_future():
    formula = 'F([5])'
    test_cases = [(formula, ['5'], True),
                  (formula, ['4'], False),
                  (formula, ['5', '4'], True),
                  (formula, ['4', '5'], True)]
    _run_cases(test_cases)


def test_path_checker_global():
    formula = 'G([5])'
    test_cases = [(formula, ['5'], True),
                  (formula, ['4'], False),
                  (formula, ['5', '4'], False),
                  (formula, ['5', '5'], True)]
    _run_cases(test_cases)


@unittest.skip('skip since formula parser can\'t handle this yet')
def test_path_checker_future_order():
    formula = 'F([4]&F([5]))'
    test_cases = [(formula, ['5'], False),
                  (formula, ['4'], False),
                  (formula, ['5', '4'], False),
                  (formula, ['4', '6', '5'], True),
                  (formula, ['2', '4', '6', '5'], True),
                  (formula, ['2', '4', '6', '5', '8'], True),
                  (formula, ['4', '5'], True)]
    _run_cases(test_cases)


def test_path_checker_online_atomic():
    formula = '[5]'
    pc = PathChecker(formula)
    tf = pc.update('5', False)
    assert tf is True, tf
    pc = PathChecker(formula)
    tf = pc.update('4', True)
    assert tf is False, tf


def test_path_checker_online_future():
    formula = 'F([5])'
    pc = PathChecker(formula)
    tf = pc.update('5', False)
    assert tf is True, tf
    pc = PathChecker(formula)
    tf = pc.update('4', False)
    assert tf is None, tf
    tf = pc.update('5', True)
    assert tf is True, tf


def test_hypothesis_tester():
    ht = HypothesisTester(0.8, 0.1, 0.1, 0.01)
    res = ht.test([True] * 10)
    assert res is None, res
    res = ht.test([True] * 100)
    assert res == 0, res
    res = ht.test([True] * 50 + [False] * 50)
    assert res == 1, res
    res = ht.test([False] * 50)
    assert res == 1, res


def test_pg_hypothesis_checking_batch():
    g_uns = nx.DiGraph()
    g_uns.add_edges_from((('A', 'B'), ('A', 'C'), ('C', 'D'), ('B', 'D'),
                          ('D', 'B'), ('D', 'C'), ('B', 'E'), ('C', 'E')))
    # For reference, these are the paths in this graph
    # [('A', 'B', 'D', 'B', 'E'),
    #  ('A', 'B', 'D', 'C', 'E'),
    #  ('A', 'C', 'D', 'B', 'E'),
    #  ('A', 'C', 'D', 'C', 'E')])
    # with 3 of them containing 'B' and one not containing 'B'
    source, target, length = ('A', 'E', 4)
    pg = PathsGraph.from_graph(g_uns, source, target, length)

    # We want to check that B is on the path somewhere
    formula = 'F([B])'
    # We set up a hypothesis test saying that we want to verify that
    # the formula is True with at least 0.2 probability (i.e. the probability
    # that a randomly samples path satisfies the formula). We allow
    # a Type-I error rate of 0.1 and Type-II error rate of 0.1, and use
    # a 0.01 indifference parameter around the value 0.2.
    ht = HypothesisTester(0.2, 0.1, 0.1, 0.01)
    # We next sample paths one by one until we can decide the hypothesis test
    samples = []
    while True:
        # Sample one path
        path = pg.sample_paths(1)[0]
        # Verify the path
        pc = PathChecker(formula, path)
        samples.append(pc.truth)
        # Check if the samples so far are sufficient to decide the hypothesis
        # and stop sampling if they are
        hyp = ht.test(samples)
        if hyp is not None:
            break
    assert hyp == 0


def test_path_hypothesis_checking_online():
    # Assume these are the paths we sampled
    paths = [
        ['1', '2', '3', '5'],
        ['1', '5', '2', '3'],
        ['5', '2', '3', '4'],
        ['1', '2', '3', '4'],
        ['5', '2', '3', '1'],
    ]
    # The formula we are looking for is that 5 is on the path
    formula = 'F([5])'
    # We set up a hypothesis test for the formula being satisfied on at least
    # 50% of the paths
    ht = HypothesisTester(0.5, 0.1, 0.1, 0.01)
    samples = []
    while True:
        pc = PathChecker(formula)
        path = random.choice(paths)
        for idx, node in enumerate(path):
            tf = pc.update(node, idx == len(path)-1)
            if tf is not None:
                break
        print(path, tf)
        samples.append(tf)
        hyp = ht.test(samples)
        if hyp is not None:
            break
    assert hyp == 0


