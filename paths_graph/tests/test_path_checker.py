import unittest
from paths_graph.path_checker import PathChecker
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
