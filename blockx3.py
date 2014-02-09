"""solve block"""
import copy

DEBUG = 1
# equal or greater WIPE_NUM block will wipe
WIPE_NUM = 3
COLOR_NUM = 4

EMPTY = 0
RED = 1
BLUE = 2
WHITE = 4
ALL_COLOR = RED | BLUE | WHITE

HOLD = 16
LEFT = 32
UP = 64
RIGHT = 128
DOWN = 256
# MAX_POS: each block multiply this for hashing
MAX_POW = 1024

class Block(object):
    """block class"""
    def __init__(self, attr, x, y):
        """attr: block is BLUE or LEFT or something"""
        self.color = attr & ALL_COLOR
        self.attr = attr >> COLOR_NUM
        self.x = x
        self.y = y

class Step(object):
    """record step"""
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.dir = dir


def init_map(p_qb):
    """init map"""
    # map of block
    l_mb = []
    # init a list[H][W]
    for _ in range(H):
        l_t = []
        for _ in range(W):
            l_t.append(EMPTY)
        l_mb.append(l_t)

    for l_b in p_qb:
        l_mb[l_b.x][l_b.y] = l_b.color | l_b.attr
    return l_mb

def print_map(p_mb):
    """print map"""
    for i in range(len(p_mb)):
        for j in range(len(p_mb[i])):
            l_s = block_str(p_mb[i][j])
            print l_s,
        print
    print '='*13

def print_step(p_step):
    """print step solved"""
    while len(p_step) > 0:
        cur_step = p_step.pop(0)
        print cur_step.x, cur_step.y,
        if UP == cur_step.dir:
            print "UP"
        elif DOWN == cur_step.dir:
            print "DOWN"
        elif LEFT == cur_step.dir:
            print "LEFT"
        elif RIGHT == cur_step.dir:
            print "RIGHT"


def block_str(p_b):
    """print a block attribute"""
    ret = ""
    color = p_b & ALL_COLOR
    if color & RED == RED:
        ret = "R"
    elif color & BLUE == BLUE:
        ret = "B"
    elif color & WHITE == WHITE:
        ret = "W"
    else:
# block is show 7x 8x
        color = color - 70
        ret = "X"
    color = color + 70
    ret = "%02d" % color

    attr = p_b >> COLOR_NUM

    if attr == HOLD:
        ret = ret + "H"
    elif attr == LEFT:
        ret = ret + "<"
    elif attr == UP:
        ret = ret + "^"
    elif attr == RIGHT:
        ret = ret + ">"
    elif attr == DOWN:
        ret = ret + "V"
    else:
        ret = ret + " "
    return ret

G_DX = {UP:-1, DOWN:1, LEFT:0, RIGHT:0}
G_DY = {LEFT:-1, RIGHT:1, UP:0, DOWN: 0}
def move(p_mb, p_x, p_y, p_dir):
    """move a step
    p_mb: matrix of block
    p_x, p_y: need to move block
    p_dir: UP,DOWN,LEFT,RIGHT
    +------>y(5)
    |
    |
    |
    |
    V
    x(9)
    """
    if p_dir != UP and p_dir != DOWN and p_dir != LEFT and p_dir != RIGHT:
        print "invalid move"
        return p_mb
    l_new_x = p_x + G_DX[p_dir]
    l_new_y = p_y + G_DY[p_dir]
# need to swap x to y
    if l_new_x < 0 or l_new_x >= H:
        print "out of range y"
        return p_mb
    if l_new_y < 0 or l_new_y >= W:
        print "out of range x"
        return p_mb
    if p_mb[p_x][p_y] & ALL_COLOR == EMPTY:
        print "moved block is empty"
        return p_mb
    if p_mb[p_x][p_y] & HOLD == HOLD or p_mb[l_new_x][l_new_y] & HOLD == HOLD:
        print "can not move HOLD"
        return p_mb
    if p_mb[p_x][p_y] == p_mb[l_new_x][l_new_y]:
        print "no need move same color"
        return p_mb

    l_tmp_b = p_mb[p_x][p_y]
    p_mb[p_x][p_y] = p_mb[l_new_x][l_new_y]
    p_mb[l_new_x][l_new_y] = l_tmp_b
    if DEBUG:
        print_map(p_mb)
    p_mb = check_map(p_mb, 3, 4, LEFT)
    if DEBUG:
        print_map(p_mb)
    return p_mb

def check_map(p_mb, p_x, p_y, p_dir):
    """check the map, whether there are some blocks line
    p_mb: map of block
    x,y: current two swap block for hint
"""
    if p_dir != UP and p_dir != DOWN and p_dir != LEFT and p_dir != RIGHT:
        print "invalid move"
        return p_mb
    p_x1 = p_x
    p_y1 = p_y
    p_x2 = p_x + G_DX[p_dir]
    p_y2 = p_y + G_DY[p_dir]
    remove1 = check_cross(p_mb, p_x1, p_y1)
    remove2 = check_cross(p_mb, p_x2, p_y2)
    for l_r in remove1:
        p_mb[l_r[0]][l_r[1]] = EMPTY
    for l_r in remove2:
        p_mb[l_r[0]][l_r[1]] = EMPTY
    return p_mb

def check_cross(p_mb, p_x, p_y):
    """check a block up,down,left,right for a line"""
    ret = []

    color = p_mb[p_x][p_y] & ALL_COLOR
    if color == EMPTY:
        return ret
    while color:
        # pick a color
        t_color = color - (color & (color - 1))
        color = color - t_color
# check UP
        xcnt = 0
        retx = []
        for i in range(p_x, 0, -1):
            if p_mb[i][p_y] & t_color == t_color:
                xcnt = xcnt + 1
                l_t = [i, p_y]
                retx.append(l_t)
            else:
                break
# check DOWN
        for i in range(p_x+1, H):
            if p_mb[i][p_y] & t_color == t_color:
                xcnt = xcnt + 1
                l_t = [i, p_y]
                retx.append(l_t)
            else:
                break
        if xcnt >= WIPE_NUM:
            ret = ret + retx

# check LEFT
        ycnt = 0
        rety = []
        for j in range(p_y, 0, -1):
            if p_mb[p_x][j] & t_color == t_color:
                ycnt = ycnt + 1
                l_t = [p_x, j]
                rety.append(l_t)
            else:
                break
# check RIGHT
        for j in range(p_y+1, W):
            if p_mb[p_x][j] & t_color == t_color:
                ycnt = ycnt + 1
                l_t = [p_x, j]
                rety.append(l_t)
            else:
                break
        if ycnt >= WIPE_NUM:
            ret = ret + rety
    return ret

def check_done(p_mb):
    """check game done"""
    for i in range(H):
        for j in range(W):
            if p_mb[i][j] & ALL_COLOR != EMPTY:
                return False
    return True

def hash_matrix(p_mb):
    """hash the matrix to a integer"""
    ret = 0
    for i in range(H):
        for j in range(W):
            ret = ret * MAX_POW + p_mb[i][j]
    return ret

def get_block(p_mb):
    """get a queue of block from a matrix of block"""
    ret = []
    for i in range(len(p_mb)):
        for j in range(len(p_mb[i])):
            if p_mb[i][j] > 0:
                ret.append(Block(p_mb[i][j], i, j))
    return ret

def bfs(p_mb, p_step_max):
    """bfs to solve"""
    l_queue = []
    l_queue.append(p_mb)
# record all step
    l_q_step = [[]]
    l_vi = []
    l_vi.append(hash_matrix(p_mb))
    while len(l_queue) > 0:
        cur_mb = l_queue.pop(0)
        cur_step = l_q_step.pop(0)
        if len(cur_step) >= p_step_max:
            print "no solve in", p_step_max, "step(s)"
            break
# get all block that can maybe moved
        l_qb = get_block(cur_mb)
        for cur_b in l_qb:
            for dir in [LEFT, RIGHT, UP, DOWN]:
                tmp_mb = copy.deepcopy(cur_mb)
                tmp_step = cur_step[:]
                #print "step: ", cur_b.x, cur_b.y, dir
                tmp_mb = move(tmp_mb, cur_b.x, cur_b.y, dir)
                new_hash = hash_matrix(tmp_mb)
                if new_hash not in l_vi:
                    tmp_step.append(Step(cur_b.x, cur_b.y, dir))
                    if check_done(tmp_mb):
                        print_step(tmp_step)
                        return 
                    l_vi.append(new_hash)
                    l_q_step.append(tmp_step)
                    l_queue.append(tmp_mb)

W = 5
H = 9

def main():
    """main function"""
    # queue of block, record all block
    g_qb = [
        Block(BLUE, 1, 3),
        Block(BLUE, 2, 3),
        Block(BLUE|RED|WHITE, 3, 4),
        Block(RED, 3, 2),
        Block(RED, 3, 1),
        Block(WHITE, 4, 3),
        Block(WHITE, 5, 3),
    ]
    step_max = 1
    g_mb = init_map(g_qb)
    bfs(g_mb, step_max)

if __name__ == "__main__":
    main()
