
class Point:
    def __init__(self, x, y):
        self.x = x * 1.0
        self.y = y * 1.0

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        if abs(self.p2.y - self.p1.y) < 0.001:
            self.p1.y = self.p1.y + 0.001
        if abs(self.p2.x - self.p1.x) < 0.001:
            self.p1.x = self.p1.x + 0.001
        self.slope = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)
        self.ord = self.p1.y - (self.slope*self.p1.x)

class Rectangle:
    def __init__(self, a, b, width, height):
        self.line1 = Line(Point(a, b), Point(a + width, b))
        self.line2 = Line(Point(a, b), Point(a, b + height))
        self.line3 = Line(Point(a + width, b), Point(a + width, b + height))
        self.line4 = Line(Point(a, b + height), Point(a + width, b + height))
        self.lines = [self.line1, self.line2, self.line3, self.line4]

def getIntersection(line1, line2):
    x = (line2.ord - line1.ord) * 1.0/ (line1.slope - line2.slope)
    y = (line1.slope * x * 1.0) + line1.ord
    print (x, y)
    return pointIsContainedInSegment(line1, x, y) and pointIsContainedInSegment(line2, x, y)

def pointIsContainedInSegment(line, x, y):
        if line.p1.x >= line.p2.x:
            maxx = line.p1.x
            minx = line.p2.x
        else:
            maxx = line.p2.x
            minx = line.p1.x
        if line.p1.y > line.p2.y:
            maxy = line.p1.y
            miny = line.p2.y
        else:
            maxy = line.p2.y
            miny = line.p1.y
        if x > minx and x < maxx and y > miny and y < maxy:
            return True
        else:
            return False

def getIntersectionLR(line1, rect):
    for line2 in rect.lines:
        result = getIntersection(line1, line2)
        if result == True:
            return True
        else:
            continue
    return False

#r = Rectangle(0, 0, 10, 20)
#l = Line(Point(11, 0), Point(20, 20))
#print getIntersectionLR(l, r)
