import pygame
from pygamehelper import *
from pygame import *
from pygame.locals import *
from math import e, pi, cos, sin, sqrt
from random import uniform

class Agent:
    def __init__(self, width):
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.width = width

    # Go to target at a certain speed
    def goToTarget(self, speed):
        dir = Vector2(self.target - self.pos)
        if dir.length() > 3:
            self.pos = self.pos + speed*dir.normalize()

    def findPath(self, navgraph):
        posclosest = findClosestPoint(self.pos, navgraph)
        tarclosest = findClosestPoint(self.target, navgraph)
        path = astar(Node(None, posclosest), Node(None, tarclosest), navgraph)
        return path

    def astar(initial, goal, graph):
        q = []

    def findClosestPoint(self, pos, navgraph):
        closest = Vector2(navgraph.gpoints[0])
        cdistance = pos.distance_to(closest)
        for p in navgraph.gpoints:
            vp = Vector2(p)
            if pos.x != vp.x and pos.y != vp.y:
                if pos.distance_to(vp) < cdistance:
                    closest = vp
                    cdistance = pos.distance_to(vp)
        return closest

class Node:
    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos


class AgentGroup:
    def __init__(self, n, w, h, navgraph):
        self.agents = []
        for i in range(n):
            a = Agent(int(uniform(15,20)))
            a.pos = Vector2(uniform(0, w), uniform(0, h))
            #a.pos = Vector2(uniform(300, 500), uniform(200, 400))
            a.target = Vector2(uniform(0, w), uniform(0, h))
            #a.target = Vector2(a.pos.x, a.pos.y)
            self.agents.append(a)
            print a.findClosestPoint(a.pos, navgraph)
            print a.findClosestPoint(a.target, navgraph)

        self.selected = self.agents[0]

    def updatePositions(self):
        for a in self.agents:
            a.goToTarget(3)

    def handleCollisions(self):
        for a in self.agents:
            for a2 in self.agents:
                if a == a2:
                    continue
                else:
                    d = a.pos.distance_to(a2.pos)
                    if d < 40:
                        overlap = 40 - d
                        dir = Vector2(a2.pos - a.pos)
                        dir.scale_to_length(overlap/2)
                        a2.pos = a2.pos + dir
                        a.pos = a.pos - dir

    def changeSelectedAgent(self, pos):
        for a in self.agents:
            if a.pos.distance_to(Vector2(pos)) < 20:
                self.selected = a

    def updateAgentTarget(self, pos):
        self.selected.target = Vector2(pos)

    def drawAgents(self, screen):
        # Draw all agents
        for a in self.agents:
            pygame.draw.circle(screen, (255,0,0), (int(a.target.x), int(a.target.y)), 30, 1)
            pygame.draw.circle(screen, (0,0,0), (int(a.pos.x), int(a.pos.y)), a.width+1)

            # Distinguish between the selected agent and the other ones
            if a == self.selected:
                pygame.draw.circle(screen, (200,250,255), (int(a.pos.x), int(a.pos.y)), a.width)
            else:
                pygame.draw.circle(screen, (200,200,255), (int(a.pos.x), int(a.pos.y)), a.width)

class NavGraph:
    def __init__(self, adjmatrix, gpoints):
        self.adjmatrix = adjmatrix
        self.gpoints = gpoints

    def neighbors(self, vertex):
        for i in range(len(self.gpoints)):
            vp = Vector2(self.gpoints[i])
            if vertex.x == vp.x and vertex.y == vp.y:
                neighbors = []
                for j in range(len(self.adjmatrix[i])):
                    if self.adjmatrix[i][j] == 1:
                        neighbors.append(self.gpoints[j])
                    return neighbors
        return None


    def drawGraph(self, screen):
        i = 0
        for i in range(len(self.gpoints)):
            pygame.draw.circle(screen, (255, 0, 255), self.gpoints[i], 10)
            for k in range(len(self.gpoints)):
                if self.adjmatrix[i][k] == 1:
                    pygame.draw.line(screen, (0, 0, 0), self.gpoints[i], self.gpoints[k], 1)



class Simulation(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        # Initialize navigation graph
        adjmatrix = [[1,1,0,0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,0,0,0,0,0,0,0,0],
        [0,1,1,0,0,0,0,0,0,0,0,0,0],[0,1,0,1,0,0,0,0,0,1,1,0,0],
        [0,1,0,0,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,0,0,0,0],[0,0,0,1,0,0,0,0,0,1,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,1,1,1],[0,0,0,0,0,0,0,0,0,0,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,1]]
        gpoints = [(400,500),(400,300),(400,100),(300,300),(600,400),(600,200),
        (700,300),(700,200),(700,100),(200,100),(200,300),(100,200),(100,500)]
        self.navgraph = NavGraph(adjmatrix, gpoints)

        # Initiliaze list of agents
        self.agents = AgentGroup(1, self.w, self.h, self.navgraph)

    def update(self):
        # Update position of agents
        #self.agents.updatePositions()

        # Handle collisions between agents
        self.agents.handleCollisions()

    def keyUp(self, key):
        pass

    def mouseUp(self, button, pos):
        if button == 3:
            self.agents.updateAgentTarget(pos)
        elif button == 1:
            self.agents.changeSelectedAgent(pos)

    def mouseMotion(self, buttons, pos, rel):
        pass

    def draw(self):
        self.screen.fill((255,255,255))

        # Draw all agents
        self.agents.drawAgents(self.screen)

        # Draw NavGraph
        self.navgraph.drawGraph(self.screen)

s = Simulation()
s.mainLoop(40)
