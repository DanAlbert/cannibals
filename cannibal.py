from collections import deque
import sys

USAGE = ('usage: python cannibals.py START END MODE OUTPUT\n' +
         'MODES: bfs, dfs, iddfs, astar')

MAX_DEPTH = 1000


class StateFile(object):
    FORMAT = """<left missionaries>,<left cannibals>,<left boats>
    <right missionaries>,<right cannibals>,<right boats>"""

    def __init__(self, file_name):
        self.file_name = file_name
        self.read_file()

    def read_file(self):
        with open(self.file_name, 'r') as state_file:
            lines = state_file.readlines()
            if len(lines) != 2:
                raise RuntimeError(self.FORMAT)
            try:
                left_bank = lines[0].split(',')
                right_bank = lines[1].split(',')
                l_missionaries, l_cannibals, l_boats = map(int, left_bank)
                r_missionaries, r_cannibals, r_boats = map(int, right_bank)
            except ValueError:
                raise RuntimeError(self.FORMAT)

            self.state = State(
                    l_cannibals,
                    l_missionaries,
                    l_boats,
                    r_cannibals,
                    r_missionaries,
                    r_boats)


class State(object):
    def __init__(self, lc, lm, lb, rc, rm, rb, previous=None):
        self.left_cannibals = lc
        self.left_missionaries = lm
        self.left_boats = lb
        self.right_cannibals = rc
        self.right_missionaries = rm
        self.right_boats = rb
        self.previous = previous
#        self.g_score = float('inf')

    def fails(self):
        return ((self.left_cannibals > self.left_missionaries and
                 self.left_missionaries > 0) or
                (self.right_cannibals > self.right_missionaries and
                 self.right_missionaries > 0))

    def expand(self):
        if self.right_boats + self.left_boats != 1:
            raise NotImplementedError('Solution only handles single boats')

        move = None
        cannibals = 0
        missionaries = 0
        if self.right_boats:
            move = self.move_left
            cannibals = self.right_cannibals
            missionaries = self.right_missionaries
        elif self.left_boats:
            move = self.move_right
            cannibals = self.left_cannibals
            missionaries = self.left_missionaries
        else:
            raise RuntimeError('No boats')

        states = []
        if missionaries > 0:
            states.append(move(missionaries=1))
        if missionaries > 1:
            states.append(move(missionaries=2))
        if cannibals > 0:
            states.append(move(cannibals=1))
        if cannibals > 0 and missionaries > 0:
            states.append(move(cannibals=1, missionaries=1))
        if cannibals > 1:
            states.append(move(cannibals=2))
        return states

    def move_left(self, missionaries=0, cannibals=0):
        if missionaries + cannibals > 2 or missionaries + cannibals < 1:
            raise RuntimeError('Invalid move')

        return State(
                self.left_cannibals + cannibals,
                self.left_missionaries + missionaries,
                self.left_boats + 1,
                self.right_cannibals - cannibals,
                self.right_missionaries - missionaries,
                self.right_boats - 1,
                previous=self)

    def move_right(self, missionaries=0, cannibals=0):
        if missionaries + cannibals > 2 or missionaries + cannibals < 1:
            raise RuntimeError('Invalid move')

        return State(
                self.left_cannibals - cannibals,
                self.left_missionaries - missionaries,
                self.left_boats - 1,
                self.right_cannibals + cannibals,
                self.right_missionaries + missionaries,
                self.right_boats + 1,
                previous=self)

    def __eq__(self, other):
        return (self.left_cannibals == other.left_cannibals and
                self.left_missionaries == other.left_missionaries and
                self.left_boats == other.left_boats and
                self.right_cannibals == other.right_cannibals and
                self.right_missionaries == other.right_missionaries and
                self.right_boats == other.right_boats)

    def __str__(self):
        return '%d,%d,%d\n%d,%d,%d' % (
                self.left_missionaries,
                self.left_cannibals,
                self.left_boats,
                self.right_missionaries,
                self.right_cannibals,
                self.right_boats)


class BfsFringe(deque):
    def pop(self):
        return super(BfsFringe, self).popleft()


class DfsFringe(list):
    pass


def solve(start_state, goal_state, mode):
    if mode == 'bfs':
        return solve_bfs(start_state, goal_state)
    elif mode == 'dfs':
        return solve_dfs(start_state, goal_state)
    elif mode == 'iddfs':
        return solve_iddfs(start_state, goal_state)
    elif mode == 'astar':
        return solve_astar(start_state, goal_state)
    else:
        raise ValueError('invalid mode: %s' % mode)


def solve_bfs(start_state, goal_state):
    fringe = BfsFringe()
    fringe.append(start_state)
    return graph_search(fringe, goal_state)


def solve_dfs(start_state, goal_state):
    fringe = DfsFringe()
    fringe.append(start_state)
    return graph_search(fringe, goal_state)


def graph_search(fringe, goal_state):
    visited = []
    while fringe:
        node = fringe.pop()
        if node == goal_state:
            return node
        if node.fails():
            continue
        if node in visited:
            continue
        visited.append(node)
        fringe.extend(node.expand())
    return None


def solve_iddfs(start_state, goal_state):
    for depth_limit in range(1, MAX_DEPTH):
        result = dls(start_state, goal_state, depth_limit, [])
        if result:
            return result
    return None


def dls(node, goal_state, depth, visited):
    if node.fails():
        return None
    elif depth == 0 and node == goal_state:
        return node
    elif depth > 0:
        visited.append(node)
        for child in node.expand():
            if child not in visited:
                result = dls(child, goal_state, depth - 1, visited)
                if result:
                    return result
        return None
    else:
        return None
    raise RuntimeError("shouldn't be here")


def cost_estimate(node1, node2):
    return 1


def distance(node1, node2):
    return 1


def solve_astar(start_state, goal_state):
    visited = []

    start_state.g_score = 0
    estimate = cost_estimate(start_state, goal_state)
    start_state.f_score = start_state.g_score + estimate

    fringe = [start_state]

    while fringe:
        current = fringe[0]
        for node in fringe[1:]:
            if node.f_score < current.f_score:
                current = node

        fringe.remove(current)
        visited.append(current)
        print "visiting"
        print
        print current
        print

        if current == goal_state:
            return node

        if current.fails():
            continue

        for node in current.expand():
            tentative_g_score = current.g_score + distance(current, node)

            # the neighbor node might not have a g_score yet
            # it will if it has already been visited, so pull that
            # if not, generate a high number to compare against
            try:
                node.g_score
            except AttributeError:
                node.g_score = next((x for x in visited if x == node),
                                    [float('inf')])

            if node in visited:
                if tentative_g_score >= node.g_score:
                    continue

            if node not in fringe or tentative_g_score < node.g_score:
                node.g_score = tentative_g_score
                node.f_score = node.g_score + cost_estimate(node, goal_state)
                if node not in fringe:
                    fringe.append(node)
    return None


def main():
    try:
        start, goal, mode, out = sys.argv[1:]
    except ValueError:
        sys.exit(USAGE)

    if mode not in ('bfs', 'dfs', 'iddfs', 'astar'):
        sys.exit(USAGE)

    start_state = StateFile(start).state
    goal_state = StateFile(goal).state

    #with open(out, 'w') as output:
    with sys.stdout as output:
        print >> output, 'start:'
        print >> output, start_state
        print >> output
        print >> output, 'goal:'
        print >> output, goal_state
        print >> output

        try:
            solution = solve(start_state, goal_state, mode)
            if solution:
                solution_list = []
                current = solution
                while current:
                    solution_list.append(current)
                    current = current.previous
                solution_list.reverse()

                print >> output, ('Solution found, %d moves' % 
                                  (len(solution_list) - 1))

                for sol in solution_list:
                    print >> output, sol
                    print >> output
        except NotImplementedError:
            sys.exit('%s is not yet implemented' % mode)

if __name__ == '__main__':
    main()
