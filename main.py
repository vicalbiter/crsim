import pygame
from pygamehelper import *
from pygame import *
from pygame.locals import *
from math import e, pi, cos, sin, sqrt
from random import uniform

class Agent:
    def __init__(self, width):
        #self.prevpos = Vector(0, 0)
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.width = width
        self.goalStack = []
        self.goal = None
        self.priority = 0

    # Go to target at a certain speed
    def goToTarget(self, target, speed):
        dir = Vector2(target - self.pos)
        if dir.length() > 3:
            self.pos = self.pos + speed*dir.normalize()
        else:
            if len(self.goalStack) != 0:
                self.goal = self.goalStack.pop()


    def planPathTo(self, target, navgraph):
        path = self.findPath(target, navgraph)
        for p in path:
            self.goalStack.insert(0,("goto", p))
        if len(self.goalStack) != 0:
            self.goal = self.goalStack.pop()

    def performTask(self, goal):
        if goal[0] == "goto":
            self.goToTarget(goal[1], 3)

    def findPath(self, target, navgraph):
        posclosest = self.findClosestPoint(self.pos, navgraph)
        tarclosest = self.findClosestPoint(self.target, navgraph)
        path = self.bfs(Node(None, posclosest), Node(None, tarclosest), navgraph)
        path.append(self.target)
        return path

    def bfs(self, initial, goal, navgraph):
        q = []
        current = initial
        visited = []
        for i in range(len(navgraph.gpoints)):
            visited.append(False)

        while current.pos.x != goal.pos.x or current.pos.y != goal.pos.y:
            neighbors = navgraph.neighbors(current.pos)
            for p in neighbors:
                idp = self.getID(p, navgraph.gpoints)
                if visited[idp] == False:
                    q.insert(0, Node(current, p))
                    visited[idp] = True
            current = q.pop()
        path = []
        while current != None:
            path.insert(0, current.pos)
            current = current.parent
        return path

    def getID(self, p, gpoints):
        for point in range(len(gpoints)):
            tp = Vector2(gpoints[point])
            if p.x == tp.x and p.y == tp.y:
                return point
        return 0

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

class Node:
    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos


class AgentGroup:
    def __init__(self, n, w, h, navgraph):
        self.agents = []
        for i in range(n):
            a = Agent(int(uniform(10,10)))
            a.pos = Vector2(uniform(0, w), uniform(0, h))
            #a.prevpos = Vector2(a.pos.x, a.pos.y)
            #a.pos = Vector2(uniform(300, 500), uniform(200, 400))
            #a.target = Vector2(uniform(0, w), uniform(0, h))
            a.target = Vector2(710, 500)
            #a.target = Vector2(a.pos.x, a.pos.y)
            a.priority = i
            self.agents.append(a)

        self.selected = self.agents[0]

        # Push "go to target" goals into the agent's behavior stack
        for a in self.agents:
            a.planPathTo(a.target, navgraph)

    # Update positions of the agents according to their last goal
    def updatePositions(self):
        for a in self.agents:
            a.performTask(a.goal)

    def handleCollisions(self):
        for a in self.agents:
            for a2 in self.agents:
                if a == a2:
                    continue
                else:
                    d = a.pos.distance_to(a2.pos)
                    if d < 20:
                        overlap = 20 - d
                        dir = Vector2(a2.pos - a.pos)
                        dir.scale_to_length(overlap/2)
                        if a.priority == a2.priority:
                            a2.pos = a2.pos + dir
                            a.pos = a.pos - dir
                        if a.priority > a2.priority:
                            a2.pos = a2.pos + dir
                            a.pos = a.pos
                        if a.priority < a2.priority:
                            a2.pos = a2.pos
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
    def __init__(self, adjmatrix, gpoints, obstacles):
        self.adjmatrix = adjmatrix
        self.gpoints = gpoints
        self.obstacles = obstacles

    def neighbors(self, vertex):
        for i in range(len(self.gpoints)):
            vp = Vector2(self.gpoints[i])
            if vertex.x == vp.x and vertex.y == vp.y:
                neighbors = []
                for j in range(len(self.adjmatrix[i])):
                    if self.adjmatrix[i][j] == 1 and i != j:
                        neighbors.append(Vector2(self.gpoints[j]))
                return neighbors
        return None

    def drawGraph(self, screen):
        i = 0
        for i in range(len(self.gpoints)):
            pygame.draw.circle(screen, (255, 0, 255), self.gpoints[i], 10)
            for k in range(len(self.gpoints)):
                if self.adjmatrix[i][k] == 1:
                    pygame.draw.line(screen, (0, 0, 0), self.gpoints[i], self.gpoints[k], 1)

    def drawObstacles(self, screen):
        i = 0
        for i in range(len(self.obstacles)):
            pygame.draw.rect(screen, (0, 0, 0), self.obstacles[i])


class Simulation(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        # Initialize navigation graph
        adjmatrix = [[1,1,0,0,0,0,0,0,0,0],[1,1,1,0,0,0,0,0,0,0],
        [0,1,1,1,1,0,0,0,0,0], [0,0,1,1,0,0,0,0,0,0], [0,0,1,0,1,1,1,1,0,0],
        [0,0,0,0,1,1,0,0,0,0], [0,0,0,0,1,0,1,0,0,0], [0,0,0,0,1,0,0,1,1,1],
        [0,0,0,0,0,0,0,1,1,0], [0,0,0,0,0,0,0,1,0,1]]

        gpoints = [(100,600), (100,500), (100, 300), (100, 100), (400, 300),
        (400, 100), (400, 500), (700,300), (700,500), (700,100)]

        obstacles = [Rect(200, 0, 100, 200), Rect(500, 0, 100, 200),
        Rect(200, 400, 100, 200), Rect(500, 400, 100, 200)]

        self.navgraph = NavGraph(adjmatrix, gpoints, obstacles)

        # Initiliaze list of agents
        self.agents = AgentGroup(10, self.w, self.h, self.navgraph)

    def update(self):
        # Update position of agents
        self.agents.updatePositions()

        # Handle collisions between agents
        self.agents.handleCollisions()

    def keyUp(self, key):
        pass

    def mouseUp(self, button, pos):
        if button == 3:
            self.agents.updateAgentTarget(pos)
            self.agents.selected.goalStack = []
            self.agents.selected.goTo(pos, self.navgraph)
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

        # Draw obstacles
        self.navgraph.drawObstacles(self.screen)

s = Simulation()
s.mainLoop(40)
