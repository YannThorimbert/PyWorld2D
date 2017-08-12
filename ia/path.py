"""
Yann Thorimbert, 04.11.2014
"""


class BranchAndBound(object):
    """
    Generic Branch & Bound strategy implementation for Least Cost Live Node List.
    """

    def __init__(self, sol, chil, g, f=None, h=None):
        """
        sol : sol(x) returns True if the state x is a solution of the problem.
        chil : chil(x) returns a list of childrens states of x.
        g : g(x) is the guide function (heuristic)
        f : you can specify f (see cost method), default is f(x) = x.
        h : you can specify h (see cost methode), defaut is h(x) = depth of x.
        """
        self.sol = sol
        self.chil = chil
        self.g = g
        if f is None:
            self.f = lambda x: x
        if h is None:
            self.h = lambda x: x.depth #by default x is a Solution instance
        self.lnl = [] #lln = Live Nodes List
        self.enode = None #enode = Expanding-Node

    def cost(self, x):
        """c(x) = f(h(x)) + g(x)"""
        return self.f(self.h(x)) + self.g(x)

    def solve(self, lnl):
        """Generic B&B solve function"""
        self.lnl = lnl
        self.enode = self.lnl.pop()
        while True:
            if self.sol(self.enode): #if solution, returns
                return self.enode
            else:
                self.lnl += self.chil(self.enode)
                if not self.lnl:
                    print("Fail")
                    return
                else:
                    #sort the lnl and reverse so that default pop function can be called
                    self.lnl.sort(key=self.cost, reverse=True)
                    #updates enode
                    self.enode = self.lnl.pop()

class State(object):
    """
    Generic datatype for storing a state.
    A state is defined by:
        - its cell
        - its parent state (i.e the (unique) state whose child is self).
        - its cost so far (note that this is redundant, since it could be computed
          from parents, but here we explicitly compute it each time a Solution
          is created).
    """

    def __init__(self, cell, parent, time_so_far):
        self.cell = cell
        self.parent = parent
        self.time_so_far = time_so_far

    def get_all_parents(self):
        if self.parent:
            return self.parent.get_all_parents() + [self.cell]
        else:
            return [self.cell]


class BranchAndBoundForMap(object):
    def __init__(self, lm, cell_i, cell_f, costs):
        self.lm = lm
        self.cell_i = cell_i
        self.cell_f = cell_f
        self.costs = costs
        self.lnl = [] #lln = Live Nodes List
        self.enode = None #enode = Expanding-Node

    def cost(self, state):
        return self.distance(state) + state.time_so_far

    def distance(self, state):
        x0,y0 = state.cell.coord
        dx = abs(x0 - self.cell_f.coord[0])
        dy = abs(y0 - self.cell_f.coord[1])
        return dx + dy

    def get_children(self, state):
        x, y = state.cell.coord
        children = []
        up = self.lm.get_cell_at(x,y-1)
        down = self.lm.get_cell_at(x,y+1)
        right = self.lm.get_cell_at(x+1,y)
        left = self.lm.get_cell_at(x-1,y)
        for cell in [up,down,right,left]:
            if cell:
                time = self.costs[cell.material.name]
                child = State(cell, state, state.time_so_far + time)
                children.append(child)
        return children

    def solve(self):
        solution = self.process()
        #
        if solution is None:
            return []
        return solution.get_all_parents()

    def process(self):
        initial_state = State(self.cell_i, None, self.costs[self.cell_i.material.name])
        self.lnl = [initial_state]
        self.enode = self.lnl.pop()
        already = set([self.enode.cell.coord])
        i = 0
        while True:
##            print(self.enode.cell.coord, self.distance(self.enode))
            if self.distance(self.enode) == 0:
                return self.enode
            else:
                if i > 1e3:
                    print("Fail")
                    return None
                self.lnl += self.get_children(self.enode)
                if not self.lnl:
                    print("Fail")
                    return
                else:
                    #sort the lnl and reverse so that default pop function can be called
                    self.lnl.sort(key=self.cost, reverse=True)
                    #updates enode
                    self.enode = self.lnl.pop()
                    while self.enode.cell.coord in already:
                        self.enode = self.lnl.pop()
                    already.add(self.enode.cell.coord)
                    i += 1


