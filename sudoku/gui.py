#!/usr/bin/python3
import pygame
import threading
pygame.init()

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class SudokuField:
    def __init__(self, n, bx, by, surface=None, cellsize=32):
        self.field = [[None for _x in range(n)] for _y in range(n)]
        self.immutable = [[False for _x in range(n)] for _y in range(n)]
        self.block = (bx, by)
        self.cellsize=cellsize
        self.selected = None
        self.select_phase = 0
        self.select_tick = 0
        self.errors = []
        self.error_ticks = 0
        self.cells = [[pygame.Rect(cellsize*_x, cellsize*_y, cellsize, cellsize) for _x in range(n)] for _y in range(n)]
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
                    if self.immutable[cell.y//self.cellsize][cell.x//self.cellsize]:
                        surface = font.render(str(value), True, pygame.Color('white'))
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
        if self.error_ticks>0:
            self.error_ticks-=1
            if self.error_ticks==0:
                x,y=self.errors[-1]
                self.field[y][x] = None
            for i in self.errors:
                pygame.draw.rect(self.surface, pygame.Color('red'), self.cells[i[1]][i[0]], 6)

    def select(self, x, y):
        for yl, l in enumerate(self.cells):
            for xl, c in enumerate(l):
                if c.collidepoint(x,y):
                    if not self.immutable[yl][xl]:
                        self.selected = (xl,yl)

    def input_number(self, number):
        if not self.selected:
            return None
        sx, sy = self.selected
        self.selected = None
        if number==None:
            self.field[sy][sx]=number
            return []
        problems = []
        n=len(self.field)
        for x in range(n):
            if self.field[sy][x]==number:
                problems.append((x,sy))
        for y in range(n):
            if self.field[y][sx]==number:
                problems.append((sx,y))
        for x in range((sx//self.block[0])*self.block[0], (sx//self.block[0] + 1)*self.block[0]):
            for y in range((sy//self.block[1])*self.block[1], (sy//self.block[1] + 1)*self.block[1]):
                if (x,y)!=(sx,sy):
                    if self.field[y][x]==number:
                        problems.append((x,y))
        problems=list(set(problems))
        if len(problems)==0:
            self.field[sy][sx]=number
        else:
            problems.append((sx,sy))

        return problems

    def show_err(self, value, number):
        self.errors = value
        x,y = value[-1]
        self.field[y][x] = number
        self.error_ticks = 30

    @classmethod
    def from_file(cls, file, surface=None, cellsize=32):
        with open(file) as f:
            data=list(map(int, f.read().split()))
        n, x, y = data[0:3]
        if x*y!=n:
            raise ValueError('Block area not equal to side length; is the file corrupt?')
        if len(data)!=n*n+3:
            raise IndexError(f'File is wrong length: expected {n*n+3} items, found {len(data)} items instead. Is the file corrupt?')
        field = cls(n,x,y, surface, cellsize=cellsize)
        data = data[3:]
        data = [None if not i else i for i in data]
        data = list(chunks(data, n))
        field.field = data
        field.immutable = [[bool(val) for val in line] for line in data]

        field.draw()
        return field

class SudokuNumberSelector:
    def __init__(self, n, surface, cellsize):
        self.surface = surface
        self.cellsize = cellsize
        self.cellnum = n
        self.cells = [pygame.Rect((i*self.cellsize,0),(self.cellsize,self.cellsize)) for i in range(n+1)]
        self.error = None
        self.error_ticks = 0
    def draw(self):
        self.surface.fill(pygame.Color('black'))
        font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize*1.5))
        for i,j in enumerate(self.cells):
            i+=1
            if i<=self.cellnum:
                text = font.render(str(i), True, pygame.Color('white'))
            else:
                text = font.render('?', True, pygame.Color('red'))
            self.surface.blit(text, j)
            pygame.draw.rect(self.surface, pygame.Color('white'), j, 2)
            if self.error == i:
                self.error_ticks-=1
                if self.error_ticks==0:
                    self.error = None
                pygame.draw.rect(self.surface, pygame.Color('red'), j, 6)

    def check_click(self, x,y):
        for i,j in enumerate(self.cells):
            if j.collidepoint(x,y):
                return i+1
    def show_err(self, num):
        self.error = num
        self.error_ticks=30





class SudokuGame:
    def __init__(self, field='field-easy.txt', cellsize=32):
        self.running = True
        self.surface = pygame.display.set_mode((800,800))
        self.width = int(open(field).readline().split()[0])
        size=self.width*cellsize
        self.fieldrect = pygame.Rect(0,0,size,size)
        self.fieldrect.x+=10
        self.fieldrect.y+=10
        self.field = SudokuField.from_file(field, pygame.Surface((size, size)), cellsize)
        self.selector = SudokuNumberSelector(len(self.field.field), pygame.Surface((size+cellsize,cellsize)), cellsize)
        self.selectorrect = self.selector.surface.get_rect()
        self.selectorrect.y = size+16+10
        self.selectorrect.x+=10

        self.clock = pygame.time.Clock()
        #self.listen_click_thread = threading.Thread(target=self.listen_click, daemon=True)
        #self.listen_click_thread.start()
    def listen_click(self):
        while self.running:
            self.clock.tick(20)
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = event.pos
                    if self.fieldrect.collidepoint((x,y)):
                        self.field.select(x-self.fieldrect.x, y-self.fieldrect.y)
                    elif self.selectorrect.collidepoint((x,y)):
                        number = self.selector.check_click(x-self.selectorrect.x, y-self.selectorrect.y)
                        if number>self.width:
                            number=None
                        value = self.field.input_number(number)
                        if value:
                            self.field.show_err(value, number)
                            self.selector.show_err(number)
    def draw(self):
        self.surface.fill(pygame.Color('black'))
        self.field.draw()
        self.selector.draw()
        self.surface.blit(self.field.surface, self.fieldrect)
        self.surface.blit(self.selector.surface, self.selectorrect)
        pygame.draw.rect(self.surface, pygame.Color('white'), self.fieldrect, 3)
        pygame.draw.rect(self.surface, pygame.Color('white'), self.selectorrect, 3)
        pygame.display.update()

if __name__ == '__main__':
    game = SudokuGame(cellsize=64)
    #input()
    game.listen_click()
