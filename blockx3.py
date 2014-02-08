from math import *

EMPTY = 0
RED = 1
BLUE = 2
WHITE = 4

HOLD = 16
LEFT = 32
UP = 64
RIGHT = 128
DOWN = 256

w = 5
h = 7

class Block:
    def __init__(self, attr, x, y):
        """
attr: block is BLUE or LEFT or something
""" 
        self.color = attr & 0xf
        self.attr = attr >> 4
        self.x = x
        self.y = y
        
""" queue of block, record all block """
qb = [
    Block(BLUE, 2, 3),
    Block(BLUE, 3, 4),
    Block(BLUE, 4, 3),
    ]

def init_map(qb):
    # map of block
    mb = []
    # init a list[h][w]
    for i in range(h):
        t = []
        for j in range(w):
            t.append(EMPTY)
        mb.append(t)
        
    for b in qb:
        mb[b.x][b.y] = b.color | b.attr
    return mb

def print_map(mb):
    for i in range(len(mb)):
        for j in range(len(mb[i])):
            s = block_str(mb[i][j])
            print s,
        print

def block_str(b):
    color = b & 0xf
    ret = ""
    if color == RED:
        ret = "R"
    elif color == BLUE:
        ret = "B"
    elif color == WHITE:
        ret = "W"
    else:
        ret = "X"

    attr = b >> 4

    if attr == HOLD:
        ret = ret + "H"
    elif attr == LEFT:
        ret = ret + "<"
    elif attr == UP:
        ret = ret + "^"
    elif attr == RIGHT:
        ret = ret + ">"
    elif attr == DOWN:
        ret.append("V")
    else:
        ret = ret + " "
    return ret

"""
check the map, whether there are some blocks line
mb: map of block
x,y: current two swap block for hint
"""
def check_map(mb, x1,y1, x2,y2):
    remove1 = check_cross(mb,x1,y1)
    remove2 = check_cross(mb,x2,y2)
    for r in remove1:
        mb[r[0]][r[1]] = EMPTY
    for r in remove2:
        mb[r[0]][r[1]] = EMPTY
    return mb

def check_cross(mb, x,y):
    xcnt = 0
    ret = []
    
    color = mb[x][y] & 0xf
    if color == EMPTY:
        return ret
    for i in range(max(x-2,0),min(x+3,h)):
        if mb[i][y] & 0xf == color:
            xcnt = xcnt + 1
            t = [i,y]
            ret.append(t)
        else:
            xcnt = 0
            ret = []
    if xcnt < 3:
        ret = []
    ycnt = 0
    rety = []
    for j in range(max(y-2,0), min(y+3,w)):
        if mb[x][j] & 0xf == color:
            ycnt = ycnt + 1
            t = [x,j]
            rety.append(t)
        else:
            ycnt = 0
            rety = []
    if ycnt >= 3:
        ret = ret + rety
    return ret
    

if __name__ == "__main__":
    mb = init_map(qb)
    print_map(mb)
    check_map(mb,2,3,0,0)
