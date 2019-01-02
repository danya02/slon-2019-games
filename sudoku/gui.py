#!/usr/bin/python3
import pygame
pygame.init()

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class SudokuField:
    def __init__(self, n, bx, by, surface=None):
        self.field = [[None for _x in range(n)] for _y in range(n)]
        self.block = (bx, by)
        self.cellsize=64
        self.selected = None
        self.select_phase = 0
        self.select_tick = 0
        self.cells = [[pygame.Rect(self.cellsize*_x, self.cellsize*_y, self.cellsize, self.cellsize) for _x in range(n)] for _y in range(n)]
        if not surface:
            self.surface = pygame.display.set_mode((n*self.cellsize, n*self.cellsize))
        else:
            self.surface = surface
    def draw(self):
        self.surface.fill(pygame.Color('black'))
        drawcell = None
        font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize*1.5))
        for fline, cline in zip(self.field, self.cells):
            for value, cell in zip(fline, cline):
                if value is None:
                    surface = font.render('?', True, pygame.Color('red'))
                else:
                    surface = font.render(str(value), True, pygame.Color('green'))
                pygame.draw.line(self.surface, pygame.Color('white'), (cell.x, 0), (cell.x, self.surface.get_height()))
                pygame.draw.line(self.surface, pygame.Color('white'), (0, cell.y), (self.surface.get_width(), cell.y))
                self.surface.blit(surface, cell)
                if self.selected:
                    if (self.selected[0]*self.cellsize, self.selected[1]*self.cellsize) ==  (cell.x, cell.y):
                        drawcell = cell
        for i in range(0,len(self.field),self.block[1]): # drawing horizontally
            pygame.draw.line(self.surface, pygame.Color('white'), (0, self.cells[i][0].y), (self.surface.get_width(), self.cells[i][0].y), 5)
        for i in range(0,len(self.field[0]),self.block[0]): # drawing vertically
            pygame.draw.line(self.surface, pygame.Color('white'), (self.cells[0][i].x, 0), (self.cells[0][i].x, self.surface.get_height()), 5)
        if drawcell:
            self.select_tick += 1
            if self.select_tick>2:
                self.select_tick=0
                self.select_phase+=1
                if self.select_phase==2:
                    self.select_phase=0
            pygame.draw.rect(self.surface, pygame.Color('red'), drawcell, [4,1][self.select_phase])

        pygame.display.update()

    def select(self, x, y):
        for yl, l in enumerate(self.cells):
            for xl, c in enumerate(l):
                if c.collidepoint(x,y):
                    self.selected = (xl,yl)

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            data=list(map(int, f.read().split()))
        n, x, y = data[0:3]
        if x*y!=n:
            raise ValueError('Block area not equal to side length; is the file corrupt?')
        if len(data)!=n*n+3:
            raise IndexError(f'File is wrong length: expected {n*n+3} items, found {len(data)} items instead. Is the file corrupt?')
        field = cls(n,x,y)
        data = data[3:]
        data = [None if not i else i for i in data]
        field.field = list(chunks(data, n))
        field.draw()
        return field
