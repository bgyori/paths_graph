import numpy
from .ltl_nodes import build_tree


class HypothesisTester(object):
    def __init__(self, prob, alpha, beta, delta):
        self.prob = prob
        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        self.logA = numpy.log((1 - self.beta) / self.alpha)
        self.logB = numpy.log(self.beta / (1 - self.alpha))

    def get_logq(self, samples):
        ps = len([s for s in samples if s])
        ns = len(samples) - ps
        term1 = ps * numpy.log(self.prob - self.delta)
        term2 = ns * numpy.log(1 - (self.prob - self.delta))
        term3 = ps * numpy.log(self.prob + self.delta)
        term4 = ns * numpy.log(1 - (self.prob + self.delta))
        logq = term1 + term2 - term3 - term4
        return logq

    def test(self, samples):
        logq = self.get_logq(samples)
        print(logq)
        if logq <= self.logB:
            return 0
        elif logq >= self.logA:
            return 1
        else:
            return -1


class PathChecker(object):
    def __init__(self, formula_str, nodes=None):
        self.formula_str = formula_str
        self.roots = []
        self.time = 0

        root = build_tree(self.formula_str)
        self.roots.append(root)

        if nodes is not None:
            for t, s in enumerate(nodes):
                tf = self.update(s, (t == (len(nodes)-1)))
                if tf is not None:
                    break
            self.truth = tf
        else:
            self.truth = None

    def update(self, x, is_last=False):
        self.roots[self.time].update(x, is_last)
        tf = self.roots[0].eval_node()
        if tf is None:
            self.roots.append(self.roots[self.time].duplicate())
            self.roots[self.time].link(self.roots[self.time+1])
        self.time += 1
        self.truth = tf
        return self.truth

