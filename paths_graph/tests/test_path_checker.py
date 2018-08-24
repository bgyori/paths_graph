from paths_graph.path_checker import PathChecker


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
