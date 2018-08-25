import numpy
from .ltl_nodes import build_tree


class HypothesisTester(object):
    """Test a hypothesis about a property based on random samples.

    The test is posed as follows. The null hypothesis H0 is that
    P_{satisfied} >= prob, and the alternative hypothesis is that
    P_{satisfied} < prob. The parameter alpha and beta define the

    Parameters
    -----------
    prob : float
        The probability threshold for the hypothesis. Between 0 and 1.
    alpha : float
        The Type-I error limit specified for deciding between the alternative
        hypotheses. Between 0 and 1.
    beta : float
        The Type-II error limit specified for deciding between the alternative
        hypotheses. Between 0 and 1.
    delta : float
        The indifference parameter, which defines an interval around `prob` in
        both directions inside which it is acceptable to conclude either of the
        alternative hypotheses.
    """
    def __init__(self, prob, alpha, beta, delta):
        self.prob = prob
        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        self.logA = numpy.log((1 - self.beta) / self.alpha)
        self.logB = numpy.log(self.beta / (1 - self.alpha))

    def get_logq(self, samples):
        """Return the logarithm of the test ratio given a set of samples.

        This function is typically not used from outside but can be useful
        for tracking and plotting how the value of the test ratio changes as
        samples are collected.

        Parameters
        ----------
        samples : list[bool]
            A list of True/False values corresponding to the satisfaction of
            a property in a series of random samples.

        Returns
        -------
        logq : float
            The test ratio calculated given the samples and test parameters.
        """
        ps = len([s for s in samples if s])
        ns = len(samples) - ps
        term1 = ps * numpy.log(self.prob - self.delta)
        term2 = ns * numpy.log(1 - (self.prob - self.delta))
        term3 = ps * numpy.log(self.prob + self.delta)
        term4 = ns * numpy.log(1 - (self.prob + self.delta))
        logq = term1 + term2 - term3 - term4
        return logq

    def test(self, samples):
        """Return the result of the hypothesis test or None of not decidable.

        Parameters
        ----------
        samples : list[bool]
            A list of True/False values corresponding to the satisfaction of
            a property in a series of random samples.

        Returns
        -------
        result : 0, 1 or None
            The result of the hypothesis test with 0 corresponding to the
            null hypothesis, 1 corresponding to the alternative hypothesis.
            If the test cannot yet be decided with the given set of samples,
            None is returned.
        """
        logq = self.get_logq(samples)
        if logq <= self.logB:
            return 0
        elif logq >= self.logA:
            return 1
        else:
            return None


class PathChecker(object):
    """Check the satisfaction of a given path property on a single path.

    The PathChecker can be used in two modes: in "offline" mode in which
    a full path has already been sampled. In this case the nodes along the path
    are passed in the constructor of the PathChecker, and the satisfaction of
    the property is determined immediately. In "online" mode, the PathChecker
    is initialized with just the property's formula and no path nodes. Nodes are
    then passed via the `update` method to the PathChecker, one by one,  and the
    `truth`  attribute can be tested after each update to see if the property
    has been verified to be False or True or has not been determined yet (None).

    Parameters
    -----------
    formula_str : str
        A path property described using BLTL.
    nodes : Optional[list]
        A list of node names corresponding to the path. Only used when the full
        path is already available at the time the PathChecker is constructed.

    Attributes
    ----------
    truth : bool or None
        This attribute needs to be monitored from outside to determine if the
        property is satisfied (1) or not satisfied (0) or could not be
        determined yet (None).
    """
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

    def update(self, node, is_last=False):
        """Return whether the property is satisfied given the latest node.

        Parameters
        ----------
        node : str
            The identifier of the next node along the path.
        is_last : bool
            Needs to be set to True if this is the last node along the path,
            otherwise False.

        Returns
        -------
        tf : bool or None
            If the property is determined to be satisfied, 1 is returned, if it
            is not satisfied, 0 is returned, if satisfaction cannot yet be
            determined, None is returned.
        """
        self.roots[self.time].update(node, is_last)
        tf = self.roots[0].eval_node()
        if tf is None:
            self.roots.append(self.roots[self.time].duplicate())
            self.roots[self.time].link(self.roots[self.time+1])
        self.time += 1
        self.truth = tf
        return self.truth

