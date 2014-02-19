"""solve block"""
import copy

DEBUG = 0
# equal or greater WIPE_NUM block will wipe
WIPE_NUM = 3
COLOR_NUM = 3

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
# block with arrow
ARROW = LEFT | UP | RIGHT | DOWN
# STOP: this block can combine with EMPTY, and stop the direction block
STOP = 512
# MAX_POS: each block multiply this for hashing
MAX_POW = 1024

class Block(object):
    """block class"""
    def __init__(self, block_type, x, y):
        """block_type: block is BLUE or LEFT or something"""
        self.block_type = block_type
        self.color = block_type & ALL_COLOR
        self.attr = block_type & ~ALL_COLOR
        self.x = x
        self.y = y

class Step(object):
    """record step"""
    def __init__(self, x, y, dirn):
        self.x = x
        self.y = y
        self.dirn = dirn


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
        ret = "X"
    ret = "%02d" % color

    attr = p_b & ~ALL_COLOR

    if attr == HOLD:
        ret = ret + "h"
    elif attr == LEFT:
        ret = ret + "<"
    elif attr == UP:
        ret = ret + "^"
    elif attr == RIGHT:
        ret = ret + ">"
    elif attr == DOWN:
        ret = ret + "v"
    elif attr == STOP:
        ret = ret + "s"
    else:
        ret = ret + " "
    return ret

def print_step(p_step):
    """print step solved"""
    while len(p_step) > 0:
        cur_step = p_step.pop(0)
        print cur_step.x, cur_step.y,
        if UP == cur_step.dirn:
            print "UP"
        elif DOWN == cur_step.dirn:
            print "DOWN"
        elif LEFT == cur_step.dirn:
            print "LEFT"
        elif RIGHT == cur_step.dirn:
            print "RIGHT"


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
        if DEBUG:
            print "invalid move"
        return p_mb
    l_new_x = p_x + G_DX[p_dir]
    l_new_y = p_y + G_DY[p_dir]
# need to swap x to y
    if l_new_x < 0 or l_new_x >= H:
        if DEBUG:
            print "out of range y"
        return p_mb
    if l_new_y < 0 or l_new_y >= W:
        if DEBUG:
            print "out of range x"
        return p_mb
    if p_mb[p_x][p_y] & ALL_COLOR == EMPTY:
        if DEBUG:
            print "moved block is empty"
        return p_mb
    if p_mb[p_x][p_y] & HOLD == HOLD or p_mb[l_new_x][l_new_y] & HOLD == HOLD:
        if DEBUG:
            print "can not move HOLD"
        return p_mb
    if p_mb[p_x][p_y] == p_mb[l_new_x][l_new_y]:
        if DEBUG:
            print "no need move same color"
        return p_mb
    if p_mb[p_x][p_y] & ARROW + p_dir == (LEFT + RIGHT) \
       or p_mb[p_x][p_y] & ARROW + p_dir == (UP + DOWN):
        if DEBUG:
            print "no need move arrow block to opponent direction"
        return p_mb

# notion: DO NOT swap the STOP attribute of block
    l_tmp_b = p_mb[p_x][p_y] & ~STOP
    p_mb[p_x][p_y] = (p_mb[p_x][p_y]&STOP) | (p_mb[l_new_x][l_new_y] & ~STOP)
    p_mb[l_new_x][l_new_y] = (p_mb[l_new_x][l_new_y]&STOP) | l_tmp_b
    if DEBUG:
        print_map(p_mb)
    while True:
        succ = do_move(p_mb)
        if not succ:
            return False
        has_wipe = False
        for i in range(H):
            for j in range(W):
                if p_mb[i][j] & ALL_COLOR > 0:
                    if check_map(p_mb, i, j):
                        has_wipe = True
                        break
            if has_wipe:
                break
        if not has_wipe:
            break
    if DEBUG:
        print_map(p_mb)
    return p_mb

def do_move(p_mb):
    """simulate the status of all blocks with arrow
    this func will update p_mb if the move valid and return True
    otherwise return False
    e.g: block move out of range, or two block crash
    """
# find all arrow block
    arrow_blk = []
    for i in range(len(p_mb)):
        for j in range(len(p_mb[i])):
            if p_mb[i][j] & ARROW > 0 and p_mb[i][j] & HOLD == 0:
                arrow_blk.append(Block(p_mb[i][j], i, j))
    while True:
# this round at least one block moved, otherwise break
        move_flag = False
        for t_blk in arrow_blk:
            old_x = t_blk.x
            old_y = t_blk.y
            if p_mb[old_x][old_y] & STOP == STOP:
                continue
            new_x = t_blk.x + G_DX[t_blk.attr & ARROW]
            new_y = t_blk.y + G_DY[t_blk.attr & ARROW]
# block lost
            if new_x < 0 or new_x >= H or new_y < 0 or new_y >= W:
                if DEBUG:
                    print "block lost at [", new_x, new_y, "]"
                return False
            if p_mb[new_x][new_y] & ALL_COLOR == 0 \
               and p_mb[new_x][new_y] & HOLD == 0:
# this block can move
                move_flag = True
                p_mb[old_x][old_y] = EMPTY
                p_mb[new_x][new_y] = p_mb[new_x][new_y] | t_blk.block_type
                t_blk.x = new_x
                t_blk.y = new_y
        if not move_flag:
            break
    return True

def check_map(p_mb, p_x, p_y):
    """check the map, whether there are some blocks line can be wipe
    p_mb: map of block
    p_x,p_y: current two swap block for hint
    p_dir: direction for hint
    return whether wipe happened
"""
    remove = check_cross(p_mb, p_x, p_y)
    for l_r in remove:
# keep STOP attribute
        p_mb[l_r[0]][l_r[1]] = p_mb[l_r[0]][l_r[1]] & STOP
    return len(remove) > 0

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
# [p_x, 0]
        for i in range(p_x, -1, -1):
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
# [p_y, 0]
        for j in range(p_y, -1, -1):
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
            if p_mb[i][j] & ALL_COLOR > 0 and p_mb[i][j] & HOLD == 0:
                ret.append(Block(p_mb[i][j], i, j))
    return ret

def bfs(p_mb, p_step_max):
    global DEBUG
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
            for dirn in [LEFT, RIGHT, UP, DOWN]:
                tmp_mb = copy.deepcopy(cur_mb)
                tmp_step = cur_step[:]
                #if len(tmp_step) == 1 and tmp_step[0].x == 2 and tmp_step[0].y == 3 and tmp_step[0].dirn == LEFT and cur_b.x == 4 and cur_b.y == 1 and dirn == RIGHT:
                #    DEBUG = 1
                succ = move(tmp_mb, cur_b.x, cur_b.y, dirn)
                #if len(tmp_step) == 1 and tmp_step[0].x == 2 and tmp_step[0].y == 3 and tmp_step[0].dirn == LEFT and cur_b.x == 4 and cur_b.y == 1 and dirn == RIGHT:
                #    raw_input()
                if not succ:
                    continue
                new_hash = hash_matrix(tmp_mb)
                if new_hash not in l_vi:
                    tmp_step.append(Step(cur_b.x, cur_b.y, dirn))
                    if check_done(tmp_mb):
                        print_step(tmp_step)
                        print "solve space has ", len(l_vi), "elems"
                        return 
                    l_vi.append(new_hash)
                    l_q_step.append(tmp_step)
                    l_queue.append(tmp_mb)
    print "solve space has ", len(l_vi), "elems"

color2num = {'R': RED, 'B': BLUE, 'W': WHITE}
type2num = {'h': HOLD, '<': LEFT, '^': UP, '>': RIGHT, 'v': DOWN, 's': STOP}
def get_block_from_file(p_file_name):
    """read game start from file
    file format:
        block_type(character) x   y
        ...
        block_type: color[color][type] e.g.: WBH WRG<
        color: RBW
        type: H<^>vs(Hold, Left, Up, Right, Down, Stop)
        return queue of block
        """
    f_in = open(p_file_name, 'r')
    ret = {}
    ret['map'] = []
    ret['step_max'] = int(f_in.readline())
    for line in f_in:
        word = line.split()
        if len(word) < 3:
            continue
        block_type = 0
        t_type = word[0][-1]
        if t_type in type2num:
            block_type = block_type | type2num[t_type]
        for color in word[0]:
            if color in color2num:
                block_type = block_type | color2num[color]
        x = int(word[1])
        y = int(word[2])
        ret['map'].append(Block(block_type, x, y))

    return ret

W = 5
H = 9

# tofix: do not handle two arrow go into the same grid
def main():
    """main function"""
    # queue of block, record all block
    """
    g_qb = [
        Block(BLUE, 1, 3),
        Block(BLUE, 2, 3),
        Block(BLUE|RED|WHITE, 3, 4),
        Block(RED, 3, 2),
        Block(RED, 3, 1),
        Block(WHITE, 4, 3),
        Block(WHITE, 5, 3),
    ]
    """
    file_name = '239.lv'
    ret = get_block_from_file(file_name)
    g_qb = ret['map']
    step_max = ret['step_max']
    g_mb = init_map(g_qb)
    print_map(g_mb)
    bfs(g_mb, step_max)

if __name__ == "__main__":
    main()
