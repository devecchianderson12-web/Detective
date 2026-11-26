import math

class Poly:

    def __init__(self, points):
        self.points = points
        self.__segments = None
        return

    def contains_point(self, x, y):
        n = len(self.points)
        inside = False
        (x1, y1) = self.points[0]
        for i in range(n + 1):
            (x2, y2) = self.points[i % n]
            if y > min(y1, y2):
                if y <= max(y1, y2):
                    if x <= max(x1, x2):
                        if y1 != y2:
                            xinters = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                        if x1 == x2 or x <= xinters:
                            inside = not inside
            x1, y1 = x2, y2

        return inside

    def cinters_segment(self, s):
        if self.contains_point(s.start[0], s.start[1]) == self.contains_point(s.end[0], s.end[1]):
            return
        elif self.__segments == None:
            self.__load_segments()
        for segment in self.__segments:
            p = segment.inters_segment(s)
            if p != None:
                return p

        return
        return

    def cinters_circle(self, c):
        if self.__segments == None:
            self.__load_segments()
        result = []
        for segment in self.__segments:
            points = c.inters_segment(segment)
            for p in points:
                result.append(p)

        return result

    def __load_segments(self):
        self.__segments = []
        if len(self.points) > 1:
            s = self.points[0]
            k = 1
            while k < len(self.points):
                e = self.points[k]
                self.__segments.append(Segment(s, e))
                s = e
                k += 1

            e = self.points[0]
            self.__segments.append(Segment(s, e))
        return


class Segment:

    def __init__(self, start, end):
        self.start = start
        self.end = end
        dx = end[0] - start[0]
        if dx == 0:
            self.m = None
            self.n = None
        else:
            self.m = float(end[1] - start[1]) / dx
            self.n = float(start[1] * end[0] - end[1] * start[0]) / dx
        return

    def contains_point(self, x, y):
        if self.m == None:
            if abs(x - self.start[0]) > 0.6:
                return False
            elif y >= self.start[1] and y <= self.end[1] or y <= self.start[1] and y >= self.end[1]:
                return True
            else:
                return False
        else:
            y0 = int(self.m * x + self.n)
            if abs(y - y0) > 0.6:
                return False
            elif (x >= self.start[0] and x <= self.end[0] or x <= self.start[0] and x >= self.end[0]) and (y >= self.start[1] and y <= self.end[1] or y <= self.start[1] and y >= self.end[1]):
                return True
            else:
                return False
        return

    def inters_segment(self, s):
        if self.m == s.m and self.n == s.n:
            x = (self.start[0] + self.end[0]) / 2
            y = (self.start[1] + self.end[1]) / 2
        elif self.m == s.m:
            return
        elif self.m == None:
            x = self.start[0]
            y = int(s.m * x + s.n)
        elif s.m == None:
            x = s.start[0]
            y = self.m * x + self.n
        else:
            x = (s.n - self.n) / (self.m - s.m)
            y = self.m * x + self.n
        if self.contains_point(x, y) and s.contains_point(x, y):
            return (
             int(x), int(y))
        else:
            return
        return


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        return

    def inters_segment(self, s):
        x1 = s.start[0] - self.center[0]
        y1 = s.start[1] - self.center[1]
        x2 = s.end[0] - self.center[0]
        y2 = s.end[1] - self.center[1]
        dx = x2 - x1
        dy = y2 - y1
        dr = math.sqrt(dx * dx + dy * dy)
        D = x1 * y2 - x2 * y1
        dr2 = dr * dr
        d = self.radius * self.radius * dr2 - D * D
        if d < 0:
            return []
        else:
            if dy < 0:
                sgndy = -1
            else:
                sgndy = 1
            Ddy = D * dy
            mDdx = -D * dx
            sgndydxsqrtd = sgndy * dx * math.sqrt(d)
            absdysqrtd = abs(dy) * math.sqrt(d)
            xa = float(Ddy + sgndydxsqrtd) / dr2 + self.center[0]
            ya = float(mDdx + absdysqrtd) / dr2 + self.center[1]
            xb = (Ddy - sgndydxsqrtd) / dr2 + self.center[0]
            yb = (mDdx - absdysqrtd) / dr2 + self.center[1]
            if d == 0 or not s.contains_point(xb, yb):
                if s.contains_point(xa, ya):
                    return [
                     (
                      int(xa), int(ya))]
                else:
                    return []
            elif s.contains_point(xa, ya):
                return [
                 (
                  int(xa), int(ya)), (int(xb), int(yb))]
            else:
                return [
                 (
                  int(xb), int(yb))]
        return


