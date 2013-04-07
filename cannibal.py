import sys

USAGE = 'usage: python cannibals.py START END MODE OUTPUT'


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
                l_missionaries, l_cannibals, l_boats = lines[0].split(',')
                r_missionaries, r_cannibals, r_boats = lines[1].split(',')
            except ValueError:
                raise RuntimeError(self.FORMAT)

            self.left_missionaries = int(l_missionaries)
            self.left_cannibals = int(l_cannibals)
            self.left_boats = int(l_boats)

            self.right_missionaries = int(r_missionaries)
            self.right_cannibals = int(r_cannibals)
            self.right_boats = int(r_boats)

    def Print(self):
        print 'left bank:'
        print 'missionaries: %d' % self.left_missionaries
        print 'cannibals: %d' % self.left_cannibals
        print 'boats: %d' % self.left_boats
        print
        print 'right bank:'
        print 'missionaries: %d' % self.right_missionaries
        print 'cannibals: %d' % self.right_cannibals
        print 'boats: %d' % self.right_boats


def main():
    try:
        start, goal, mode, out = sys.argv[1:]
    except ValueError:
        sys.exit(USAGE)

    start_state = StateFile(start)
    goal_state = StateFile(goal)

    print 'start:'
    start_state.Print()
    print
    print 'goal:'
    goal_state.Print()

if __name__ == '__main__':
    main()
