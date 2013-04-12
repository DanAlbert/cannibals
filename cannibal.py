from collections import deque
import sys


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
    def __init__(self, lc, lm, lb, rc, rm, rb):
        self.left_cannibals = lc
        self.left_missionaries = lm
        self.left_boats = lb
        self.right_cannibals = rc
        self.right_missionaries = rm
        self.right_boats = rb

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
                self.right_boats - 1)

    def move_right(self, missionaries=0, cannibals=0):
        if missionaries + cannibals > 2 or missionaries + cannibals < 1:
            raise RuntimeError('Invalid move')

        return State(
                self.left_cannibals - cannibals,
                self.left_missionaries - missionaries,
                self.left_boats - 1,
                self.right_cannibals + cannibals,
                self.right_missionaries + missionaries,
                self.right_boats + 1)

    def __eq__(self, other):
        return (self.left_cannibals == other.left_cannibals and
                self.left_missionaries == other.left_missionaries and
                self.left_boats == other.left_boats and
                self.right_cannibals == other.right_cannibals and
                self.right_missionaries == other.right_missionaries and
                self.right_boats == other.right_boats)

    def __str__(self):
        # TODO: this is pretty awful... fix the string concatenation
        str = ''
        str += 'left bank:\n'
        str += 'missionaries: %d\n' % self.left_missionaries
        str += 'cannibals: %d\n' % self.left_cannibals
        str += 'boats: %d\n' % self.left_boats
        str += '\n'
        str += 'right bank:\n'
        str += 'missionaries: %d\n' % self.right_missionaries
        str += 'cannibals: %d\n' % self.right_cannibals
        str += 'boats: %d\n' % self.right_boats
        return str


def solve(start_state, goal_state, mode):
    if mode == 'bfs':
        solve_bfs(start_state, goal_state)
    elif mode == 'dfs':
        solve_dfs(start_state, goal_state)
    elif mode == 'iddfs':
        solve_iddfs(start_state, goal_state)
    elif mode == 'astar':
        solve_astar(start_state, goal_state)
    else:
        raise ValueError('invalid mode: %s' % mode)

def solve_bfs(start_state, goal_state):
    visited = []
    fringe = deque()
    fringe.append(start_state)
    while fringe:
        node = fringe.popleft()
        print 'state:'
        print node
        if node == goal_state:
            print 'success'
            print
            return True
        if node.fails():
            print 'fails'
            print
            continue
        if node in visited:
            print 'visited'
            print
            continue
        print
        visited.append(node)
        fringe.extend(node.expand())
    return False

def solve_dfs(start_state, goal_state):
    visited = []
    fringe = [start_state]
    while fringe:
        node = fringe.pop()
        print 'state:'
        print node
        if node == goal_state:
            print 'success'
            print
            return True
        if node.fails():
            print 'fails'
            print
            continue
        if node in visited:
            print 'visited'
            print
            continue
        print
        visited.append(node)
        expanded = node.expand()
        expanded.reverse()
        fringe.extend(expanded)
    return False

def solve_iddfs(start_state, goal_state):
    raise NotImplementedError()

def solve_astar(start_state, goal_state):
    raise NotImplementedError()

USAGE = ('usage: python cannibals.py START END MODE OUTPUT\n' +
         'MODES: bfs, dfs, iddfs, astar')

def main():
    try:
        start, goal, mode, out = sys.argv[1:]
    except ValueError:
        sys.exit(USAGE)

    if mode not in ('bfs', 'dfs', 'iddfs', 'astar'):
        sys.exit(USAGE)

    start_state = StateFile(start).state
    goal_state = StateFile(goal).state

    print 'start:'
    print start_state
    print
    print 'goal:'
    print goal_state

    try:
        solve(start_state, goal_state, mode)
    except NotImplementedError:
        sys.exit('%s is not yet implemented' % mode)

if __name__ == '__main__':
    main()
