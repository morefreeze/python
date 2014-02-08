""" solve block """

EMPTY = 0
RED = 1
BLUE = 2
WHITE = 4

HOLD = 16
LEFT = 32
UP = 64
RIGHT = 128
DOWN = 256

class Block(object):
    """block class"""
    def __init__(self, attr, x, y):
        """attr: block is BLUE or LEFT or something"""
        self.color = attr & 0xf
        self.attr = attr >> 4
        self.x = x
        self.y = y


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
    color = p_b & 0xf
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

    attr = p_b >> 4

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
    if p_mb[p_x][p_y] & HOLD == HOLD or p_mb[l_new_x][l_new_y] & HOLD == HOLD:
        print "can not move HOLD"
        return p_mb
# need to swap x to y
    if l_new_x < 0 or l_new_x >= H:
        print "out of range y"
        return p_mb
    if l_new_y < 0 or l_new_y >= W:
        print "out of range x"
        return p_mb

    l_tmp_b = p_mb[p_x][p_y]
    p_mb[p_x][p_y] = p_mb[l_new_x][l_new_y]
    p_mb[l_new_x][l_new_y] = l_tmp_b
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
    xcnt = 0
    ret = []

    color = p_mb[p_x][p_y] & 0xf
    if color == EMPTY:
        return ret
    retx = []
    rety = []
    while color:
        # pick a color
        t_color = color - (color & (color - 1))
        color = color - t_color
        for i in range(max(p_x-2, 0), min(p_x+3, H)):
            if p_mb[i][p_y] & t_color == t_color:
                xcnt = xcnt + 1
                l_t = [i, p_y]
                retx.append(l_t)
            elif i > p_x:
                break
        if xcnt < 3:
            retx = []
        else:
            ret = ret + retx
        ycnt = 0
        rety = []
        for j in range(max(p_y-2, 0), min(p_y+3, W)):
            if p_mb[p_x][j] & t_color == t_color:
                ycnt = ycnt + 1
                l_t = [p_x, j]
                rety.append(l_t)
            elif j > p_y:
                break
        if ycnt < 3:
            rety = []
        else:
            ret = ret + rety
    return ret

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
    g_mb = init_map(g_qb)
    g_mb = move(g_mb, 3, 4, LEFT)
    print_map(g_mb)
    g_mb = check_map(g_mb, 3, 4, LEFT)
    print_map(g_mb)

if __name__ == "__main__":
    main()
