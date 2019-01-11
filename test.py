
class Point:
    def __init__(self, x, y):
        self.x = x * 1.0
        self.y = y * 1.0

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.slope = (p2.y - p1.y) / (p2.x - p1.x)
        self.ord = self.p1.y - (self.slope*self.p1.x)

class Rectangle:
    def __init__(self, a, b, widht, height):
        self.line1 = Line(Point(a, b), Point(a + widht, b))
        self.line2 = Line(Point(a, b), Point(a, b + height))
        self.line3 = Line(Point(a + width, b), Point(a + width, b + heigth))
        self.line4 = Line(Point(a, b + height), Point(a + width, b + height))
        self.lines = [self.line1, self.line2, self.line3, self.line4]

def getIntersection(line1, line2):
    x = (line2.ord - line1.ord) * 1.0/ (line1.slope - line2.slope)
    y = (line1.slope * x * 1.0) + line1.ord
    if line1.p1.x >= line1.p2.x:
        maxx = line1.p1.x
        minx = line1.p2.x
    else:
        maxx = line1.p2.x
        minx = line1.p1.x
    if line1.p1.y > line1.p2.y:
        maxy = line1.p1.y
        miny = line1.p2.y
    else:
        maxy = line1.p2.y
        miny = line1.p1.y
    #print (x, y)
    if x > minx and x < maxx and y > miny and y < maxy:
        return True
    else:
        return False

line1 = Line(Point(0, 0), Point(1, 1))
line2 = Line(Point(4, 0), Point(0, 2))
