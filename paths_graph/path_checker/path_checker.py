from .ltl_nodes import build_tree


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

