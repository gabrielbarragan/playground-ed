import sys
import json
import math


def _emit(cmd: dict):
    print(f"__GFX__:{json.dumps(cmd)}", flush=True)


class Turtle:
    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._angle = 90.0   # 0° = derecha, 90° = arriba (convención turtle)
        self._pen_down = True
        self._color = "#000000"
        self._fill_color = "#000000"
        self._width = 1
        self._visible = True
        _emit({"cmd": "init", "w": 600, "h": 400})

    def forward(self, distance):
        rad = math.radians(self._angle)
        x2 = self._x + distance * math.cos(rad)
        y2 = self._y - distance * math.sin(rad)
        if self._pen_down:
            _emit({"cmd": "line", "x1": self._x, "y1": self._y,
                   "x2": x2, "y2": y2, "color": self._color, "w": self._width})
        self._x, self._y = x2, y2
        _emit({"cmd": "cursor", "x": self._x, "y": self._y, "a": self._angle})

    def backward(self, distance): self.forward(-distance)
    def fd(self, d): self.forward(d)
    def bk(self, d): self.backward(d)

    def right(self, angle):
        self._angle -= angle
        _emit({"cmd": "cursor", "x": self._x, "y": self._y, "a": self._angle})

    def left(self, angle): self.right(-angle)
    def rt(self, a): self.right(a)
    def lt(self, a): self.left(a)

    def penup(self):
        self._pen_down = False

    def pendown(self):
        self._pen_down = True

    def pu(self): self.penup()
    def pd(self): self.pendown()

    def goto(self, x, y):
        if self._pen_down:
            _emit({"cmd": "line", "x1": self._x, "y1": self._y,
                   "x2": x, "y2": y, "color": self._color, "w": self._width})
        self._x, self._y = x, y
        _emit({"cmd": "cursor", "x": x, "y": y, "a": self._angle})

    def setpos(self, x, y): self.goto(x, y)
    def setx(self, x): self.goto(x, self._y)
    def sety(self, y): self.goto(self._x, y)

    def circle(self, radius, extent=360):
        _emit({"cmd": "circle", "x": self._x, "y": self._y,
               "r": radius, "extent": extent,
               "color": self._color, "w": self._width, "pen": self._pen_down})

    def color(self, *args):
        if len(args) == 1:
            self._color = self._fill_color = args[0]
        elif len(args) == 2:
            self._color, self._fill_color = args
        _emit({"cmd": "color", "stroke": self._color, "fill": self._fill_color})

    def pencolor(self, c):
        self._color = c
        _emit({"cmd": "color", "stroke": c, "fill": self._fill_color})

    def fillcolor(self, c):
        self._fill_color = c
        _emit({"cmd": "color", "stroke": self._color, "fill": c})

    def width(self, w):
        self._width = w

    def pensize(self, w): self.width(w)

    def begin_fill(self):
        _emit({"cmd": "begin_fill", "color": self._fill_color})

    def end_fill(self):
        _emit({"cmd": "end_fill"})

    def clear(self):
        _emit({"cmd": "clear"})

    def hideturtle(self):
        self._visible = False
        _emit({"cmd": "hide_cursor"})

    def showturtle(self):
        self._visible = True
        _emit({"cmd": "show_cursor"})

    def home(self):
        self.goto(0, 0)
        self._angle = 90.0

    def speed(self, s):
        pass  # no-op: el renderizado ya es instantáneo

    def done(self):
        _emit({"cmd": "done"})

    def mainloop(self):
        pass  # no-op

    def write(self, text, move=False, align="left", font=("Arial", 12, "normal")):
        _emit({"cmd": "text", "x": self._x, "y": self._y,
               "text": str(text), "font": font, "color": self._color})


# ── Screen (singleton stub) ───────────────────────────────────────────────────

class _Screen:
    """
    Stub del objeto Screen de turtle estándar.
    - bgcolor/title/setup emiten comandos GFX donde aplica.
    - tracer/update/exitonclick/mainloop son no-ops.
    """
    _instance = None

    def bgcolor(self, color):
        _emit({"cmd": "bgcolor", "color": color})

    def setup(self, width=600, height=400, startx=None, starty=None):
        _emit({"cmd": "init", "w": width, "h": height})

    def title(self, titlestring):
        pass  # no-op: no hay ventana

    def tracer(self, n=None, delay=None):
        pass  # no-op: el renderizado es instantáneo

    def update(self):
        pass  # no-op

    def exitonclick(self):
        pass  # no-op

    def mainloop(self):
        pass  # no-op

    def listen(self):
        pass  # no-op

    def onkey(self, fun, key):
        pass  # no-op

    def onkeypress(self, fun, key=None):
        pass  # no-op

    def onkeyrelease(self, fun, key=None):
        pass  # no-op

    def onclick(self, fun, btn=1, add=None):
        pass  # no-op

    def ontimer(self, fun, t=0):
        pass  # no-op


def Screen():
    if _Screen._instance is None:
        _Screen._instance = _Screen()
    return _Screen._instance


# ── API funcional (turtle usa funciones globales + instancia implícita) ────────

_t = None


def _get():
    global _t
    if _t is None:
        _t = Turtle()
    return _t


def forward(d):   _get().forward(d)
def backward(d):  _get().backward(d)
def fd(d):        _get().fd(d)
def bk(d):        _get().bk(d)
def right(a):     _get().right(a)
def left(a):      _get().left(a)
def rt(a):        _get().rt(a)
def lt(a):        _get().lt(a)
def penup():      _get().penup()
def pendown():    _get().pendown()
def pu():         _get().pu()
def pd():         _get().pd()
def goto(x, y):   _get().goto(x, y)
def setpos(x, y): _get().setpos(x, y)
def setx(x):      _get().setx(x)
def sety(y):      _get().sety(y)
def circle(r, e=360): _get().circle(r, e)
def color(*a):    _get().color(*a)
def pencolor(c):  _get().pencolor(c)
def fillcolor(c): _get().fillcolor(c)
def width(w):     _get().width(w)
def pensize(w):   _get().pensize(w)
def begin_fill(): _get().begin_fill()
def end_fill():   _get().end_fill()
def clear():      _get().clear()
def hideturtle(): _get().hideturtle()
def showturtle(): _get().showturtle()
def home():       _get().home()
def speed(s):     _get().speed(s)
def done():       _get().done()
def mainloop():   _get().mainloop()
def write(text, move=False, align="left", font=("Arial", 12, "normal")):
    _get().write(text, move, align, font)
