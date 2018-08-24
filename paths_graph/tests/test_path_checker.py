from paths_graph.path_checker import PathChecker


def test_path_checker_batch_atomic():
    formula = '[5]'
    pc = PathChecker(formula, ['5'])
    assert pc.truth == True
    pc = PathChecker(formula, ['4'])
    assert pc.truth == False
    pc = PathChecker(formula, ['5', '4'])
    assert pc.truth == True
    pc = PathChecker(formula, ['4', '5'])
    assert pc.truth == False
