import pygame
from pygamehelper import *
from pygame import *
from pygame.locals import *
from math import e, pi, cos, sin, sqrt
from random import uniform

class Agent:
    def __init__(self):
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)

    # Go to target at a certain speed
    def goToTarget(self, speed):
        dir = Vector2(self.target - self.pos)
        if dir.length() > 3:
            self.pos = self.pos + speed*dir.normalize()

class AgentGroup:
    def __init__(self, n, w, h):
        self.agents = []
        for i in range(n):
            a = Agent()
            a.pos = Vector2(uniform(0, w), uniform(0,h))
            a.target = Vector2(uniform(0, w), uniform(0, h))
            self.agents.append(a)

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
            pygame.draw.circle(screen, (0,0,0), (int(a.pos.x), int(a.pos.y)), 21)

            # Distinguish between the selected agent and the other ones
            if a == self.selected:
                pygame.draw.circle(screen, (200,250,255), (int(a.pos.x), int(a.pos.y)), 20)
            else:
                pygame.draw.circle(screen, (200,200,255), (int(a.pos.x), int(a.pos.y)), 20)

class Simulation(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        # Initiliaze list of agents
        self.agents = AgentGroup(10, self.w, self.h)

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
        elif button == 1:
            self.agents.changeSelectedAgent(pos)

    def mouseMotion(self, buttons, pos, rel):
        pass

    def draw(self):
        self.screen.fill((255,255,255))

        # Draw all agents
        self.agents.drawAgents(self.screen)

s = Simulation()
s.mainLoop(40)
