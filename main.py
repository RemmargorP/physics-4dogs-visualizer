from tkinter import *
import time
import os


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __init__(self, p1, p2):
        self.x = p2.x - p1.x
        self.y = p2.y - p1.y

    def div(self, d):
        self.x /= d
        self.y /= d

    def norm(self, length = 1.0):
        self.div(self.len() / length)

    def len(self):
        return (self.x**2 + self.y**2)**0.5


class Dog:
    def __init__(self, spd, pos=Point()):
        self.position = pos
        self.speed = spd
        self.path = [pos]

    def cpy(self):
        tmp = Dog(spd, Point())
        tmp.position.x = self.position.x
        tmp.position.y = self.position.y
        tmp.path = self.path
        return tmp

root = Tk()

field_size = 500

canvas = Canvas(root, width=field_size+10, height=field_size+10)
canvas.grid(row=0, column=0)

diagram = Canvas(root, width=field_size + 20, height = field_size / 2 + 20)
diagram.grid(column = 1, row = 0)

initialized = 0

spd = 100
dogs = []

doge_r = 3
stop = False

distances = []
runtime = 0

def init():
    global dogs, initialized, runtime, stop, distances
    dogs = []
    dogs.append(Dog(spd, Point(5, 5)))
    dogs.append(Dog(spd, Point(field_size + 5, 5)))
    dogs.append(Dog(spd, Point(field_size + 5, field_size + 5)))
    dogs.append(Dog(spd, Point(5, field_size + 5)))
    initialized = 1
    runtime = 0
    distances = []
    stop = False

def scaled(p, mnx, dx, mny, dy):
    return (p.x - mnx) / dx * field_size / 2, (p.y - mny) / dy * field_size

def draw():
    global dogs
    canvas.delete(ALL)
    for doge in dogs:
        for i in range(0, len(doge.path) - 1):
            prev, nxt = doge.path[i], doge.path[i + 1]
            canvas.create_line(prev.x, prev.y, nxt.x, nxt.y, fill='green')
    for doge in dogs:
        x = doge.position.x
        y = doge.position.y
        canvas.create_oval(x - doge_r, y - doge_r, x + doge_r, y + doge_r, fill='Blue')

    global distances
    diagram.delete(ALL)

    mndist, mxdist = 10**10, 0
    mntime, mxtime = 10**10, 0

    for i in distances:
        mndist = min(mndist, i.x)
        mxdist = max(mxdist, i.x)
        mntime = min(mntime, i.y)
        mxtime = max(mxtime, i.y)

    delta_dist = max(5, mxdist - mndist)
    delta_time = max(0.1, mxtime - mntime)

    for i in range(len(distances) - 1):
        prev, nxt = distances[i], distances[i + 1]
        prevx, prevy = scaled(prev, mndist, delta_dist, mntime, delta_time)
        nxtx, nxty = scaled(nxt, mndist, delta_dist, mntime, delta_time)
        diagram.create_line(prevy + 10, field_size / 2 - prevx + 10, nxty + 10, field_size / 2 - nxtx + 10, fill='red')
    for i in distances[::20]:
        px, py = scaled(i, mndist, delta_dist, mntime, delta_time)
        diagram.create_text(py + 10, field_size / 2 - px + 10, text="{0:.1f}".format(i.x))
eps = 1e-5


def simulate(delta_t):
    global initialized, dogs, runtime, stop, distances
    if not initialized:
        init()

    done = True
    maxdist = 0
    for i in range(0, 3):
        maxdist = max(maxdist, Vector(dogs[i].position, dogs[i + 1].position).len())

    if len(distances) == 0 or abs(distances[-1].x - maxdist) > 3: distances.append(Point(maxdist, runtime))

    done = maxdist < eps
    total_time['text'] = 'Total time: ' + "{0:.5f}".format(runtime)

    total_path_len = 0
    dpth = dogs[0].path
    for i in range(len(dpth) - 1):
        total_path_len += Vector(dpth[i], dpth[i + 1]).len()
    total_path['text'] = 'Total path length: ' + "{0:.5f}".format(total_path_len)
    if done:
        stop = True
    else:
        delta_t = min(delta_t, maxdist / spd / 40)
        runtime += delta_t

    if stop: return

    next_dogs = []
    for i in range(4):
        v = Vector(dogs[i].position, dogs[(i + 1) % 4].position)
        v.norm(spd)
        v.x *= delta_t
        v.y *= delta_t
        d = dogs[i].cpy()
        d.position.x += v.x
        d.position.y += v.y
        if Vector(d.path[-1], d.position).len() > 3:
            d.path.append(d.position)
        next_dogs.append(d)
    dogs = next_dogs


def update(delta_t):
    simulate(delta_t)
    draw()

now = time.time()
runtime = 0
UPS = 100

def restart():
    init()
restart_btn = Button(root, text='Restart', command=restart).grid(column=1, row=3)

def change_spd():
    global spd
    spd = float(spd_text.get('1.0', END))
spd_text = Text(root, height=1, width=7, font='Arial 14')
spd_text.grid(column=2, row=5)
spd_text.insert(1.0, str(spd))
spd_text_reset = Button(root, text='Change speed', command=change_spd).grid(column=3, row=5)

def change_size():
    global field_size, canvas
    field_size = float(field_size_text.get('1.0', END))

    canvas = Canvas(root, width=field_size + 10, height=field_size + 10)
    canvas.grid(row=0, column=0, rowspan=200)

field_size_text = Text(root, height=1, width=7, font='Arial 14')
field_size_text.grid(column=2, row=6)
field_size_text.insert(1.0, str(field_size))
field_size_text_reset = Button(root, text='Change size', command=change_size).grid(column=3, row=6)


total_time = Label(root)
total_time.grid(column=3, row = 15)

total_path = Label(root)
total_path.grid(column=3, row = 16)

def quit():
    os._exit(0)

quit_btn = Button(root, text='Exit', command=quit)
quit_btn.grid(column=1, row=10)

while 1:
    dt = max(time.time() - now, 1 / UPS)
    update(dt)
    root.update()

    time.sleep(max(0, 1/UPS - time.time() + now))
    now = time.time()
