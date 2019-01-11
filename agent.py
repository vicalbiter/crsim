import pygame
from geometry import *
from pygamehelper import *
from pygame import *
from pygame.locals import *
from math import e, pi, cos, sin, sqrt
from random import uniform


class Agent:
    def __init__(self, width, obstaclesR):
        #self.prevpos = Vector(0, 0)
        self.id = 0
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.width = width
        self.goalStack = []
        self.goal = None
        self.priority = 0
        self.obstacles = obstaclesR
        self.lineToTNextGoal = Line(Point(0, 0), Point(0, 0))

    # Go to target at a certain speed
    # If the agent can see its next target directly (i.e. there are no obstacles
    # in between), pop the current action from the BS
    def goToTarget(self, target):
        self.dir = Vector2(target - self.pos)
        #self.updateVelocity(dir)
        if len(self.goalStack) != 0:
            # If the next goal is within reach, skip the current goal
            nextGoal = self.goalStack[len(self.goalStack) - 1]
            self.lineToNextGoal = Line(Point(self.pos.x, self.pos.y), Point(nextGoal[1].x, nextGoal[1].y))
            for r in range(len(self.obstacles)):
                result = getIntersectionLR(self.lineToNextGoal, self.obstacles[r])
                if result == True:
                    break;
                else:
                    if r == len(self.obstacles) - 1:
                        self.goal = self.goalStack.pop()
            #l = Line(Point(pos.x, pos.y), Point())
        if self.dir.length() > 3:
            self.pos = self.pos + self.velocity
        else:
            if len(self.goalStack) != 0:
                self.goal = self.goalStack.pop()

    def updateVelocity(self, neighbors):
        self.velocity = 2.0*self.dir.normalize()
        separation = self.calculateSeparationVector(neighbors)
        velchange = separation
        if velchange.length() > 0:
            velchange.scale_to_length(0.2)
        self.velocity = self.velocity + velchange

    # Plan a bath, using BFS to a certain target, and add all the intermediate
    # steps necessary to get to that path to the behavior stack
    def planPathTo(self, target, navgraph):
        path = self.findPath(target, navgraph)
        for p in path:
            self.goalStack.insert(0,("goto", p))
        if len(self.goalStack) != 0:
            self.goal = self.goalStack.pop()

    # Perform the task at hand
    def performTask(self, goal):
        if goal[0] == "goto":
            self.goToTarget(goal[1])

    # Find a path from the current position to the target position
    def findPath(self, target, navgraph):
        posclosest = self.findClosestPoint(self.pos, navgraph)
        tarclosest = self.findClosestPoint(self.target, navgraph)
        path = self.bfs(Node(None, posclosest), Node(None, tarclosest), navgraph)
        path.append(self.target)
        return path

    # BFS algortithm to find the shortest path (assuming unitary costs) from
    # one vertex to another
    def bfs(self, initial, goal, navgraph):
        q = []
        current = initial
        visited = set([initial])
        while current.pos.x != goal.pos.x or current.pos.y != goal.pos.y:
            # Highly optimizible
            neighbors = navgraph.neighbors(current.pos)
            # Highly optimizible
            for p in neighbors:
                node = Node(current, p)
                if node not in visited:
                    q.insert(0, node)
                    visited.add(node)
            current = q.pop()
            #for p in neighbors:
            #    idp = self.getID(p, navgraph.gpoints)
            #    if visited[idp] == False:
            #        q.insert(0, Node(current, p))
            #        visited[idp] = True
            #current = q.pop()
        path = []
        while current != None:
            path.insert(0, current.pos)
            current = current.parent
        return path

    # Get the label of the vertex
    def getID(self, p, gpoints):
        for point in range(len(gpoints)):
            tp = Vector2(gpoints[point])
            if p.x == tp.x and p.y == tp.y:
                return point
        return 0

    # Find the closest vertex in the graph to a certain test point
    def findClosestPoint(self, pos, navgraph):
        closest = Vector2(navgraph.gpoints[0])
        cdistance = pos.distance_to(closest)
        for p in navgraph.gpoints:
            vp = Vector2(p)
            if pos.x != vp.x or pos.y != vp.y:
                if pos.distance_to(vp) < cdistance:
                    closest = vp
                    cdistance = pos.distance_to(vp)
        return closest

    def calculateSeparationVector(self, neighbors):
        separation = Vector2(0, 0)
        for neighbor in neighbors:
            if neighbor.pos.x == self.pos.x and neighbor.pos.y == self.pos.y:
                continue;
            distance = self.pos.distance_to(neighbor.pos)
            vector = self.pos - neighbor.pos
            vector.scale_to_length(10/distance)
            separation = separation + vector
        return separation

class Node:
    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos
