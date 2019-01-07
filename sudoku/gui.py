#!/usr/bin/python3
import pygame
import threading
import tkinter
import tkinter.filedialog
import traceback
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
        self.cellsize = cellsize
        self.n = n
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize))
        self.images_white = [self.font.render(str(i) if i>0 else '?', True, pygame.Color('white' if i>0 else 'red')) for i in range(self.n+1)]
        self.images_green = [self.font.render(str(i) if i>0 else '?', True, pygame.Color('green' if i>0 else 'red')) for i in range(self.n+1)]
        self.block = (bx, by)
        self.cellsize=cellsize
        self.selected = None
        self.select_phase = 0
        self.select_tick = 0
        self.errors = []
        self.error_ticks = 0
        self.count = 0
        self.cells = [[pygame.Rect(cellsize*_x, cellsize*_y, cellsize, cellsize) for _x in range(self.n)] for _y in range(self.n)]
        if not surface:
            self.surface = pygame.display.set_mode((n*self.cellsize, n*self.cellsize))
        else:
            self.surface = surface

    def recreate_cache(self):
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize))
        self.images_white = [self.font.render(str(i) if i>0 else '?', True, pygame.Color('white' if i>0 else 'red')) for i in range(self.n+1)]
        self.images_green = [self.font.render(str(i) if i>0 else '?', True, pygame.Color('green' if i>0 else 'red')) for i in range(self.n+1)]
        self.cells = [[pygame.Rect(self.cellsize*_x, self.cellsize*_y, self.cellsize, self.cellsize) for _x in range(self.n)] for _y in range(self.n)]

    def draw(self):
        font=self.font
        self.surface.fill(pygame.Color('black'))
        for i in self.cells:
            pygame.draw.line(self.surface, pygame.Color('white'), (0, i[0].y), (self.surface.get_width(), i[0].y))
        for i in self.cells[0]:
            pygame.draw.line(self.surface, pygame.Color('white'), (i.x, 0), (i.x, self.surface.get_height()))

        drawcell = None
        for fline, cline in zip(self.field, self.cells):
            for value, cell in zip(fline, cline):
                if value is None:
                    surface = self.images_green[0]
                else:
                    if self.immutable[cell.y//self.cellsize][cell.x//self.cellsize]:
                        surface = self.images_white[value]
                    else:
                        surface = self.images_green[value]
                tc = surface.get_rect()
                tc.center=cell.center
                self.surface.blit(surface, tc)
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
        self.count+=1
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
        self.n = n
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize))
    def reset_cache(self):
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.cellsize))
        self.cells = [pygame.Rect((i*self.cellsize,0),(self.cellsize,self.cellsize)) for i in range(self.n+1)]
    def draw(self):
        self.surface.fill(pygame.Color('black'))
        font=self.font
        for i,j in enumerate(self.cells):
            i+=1
            if i<=self.cellnum:
                text = font.render(str(i), True, pygame.Color('white'))
            else:
                text = font.render('?', True, pygame.Color('red'))
            tc = text.get_rect()
            tc.center=j.center
            self.surface.blit(text, tc)
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


class SudokuScoreCounter:
    def __init__(self, score_from, surface):
        self.target = score_from
        self.surface = surface
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        self.brect = pygame.Rect(0,0,0,0)
    def draw(self, custom=None):
        self.surface.fill(pygame.Color('black'))
        text = self.font.render(str(self.target.count), True, pygame.Color('white'))
        trect = text.get_rect()
        trect.x+=5
        trect.y+=5
        self.surface.blit(text, trect)
        text = self.font.render("Restart", True, pygame.Color('white'))
        rtrect = text.get_rect()
        rtrect.y+=5
        rtrect.x+=200+trect.x
        self.surface.blit(text, rtrect)
        pygame.draw.rect(self.surface, pygame.Color('white'), rtrect, 2)
        self.brect = rtrect
    def click(self, x, y):
        if self.brect.collidepoint((x,y)):
            for y in range(len(self.target.field)):
                for x in range(len(self.target.field)):
                    if not self.target.immutable[y][x]:
                        self.target.field[y][x]=None
            self.target.count=0

class SudokuGame:
    def __init__(self, width, height, cellsize=32):
        try:
            dimension = min(width, height)

            field = self.get_path()
            self.running = True
            self.surface = pygame.display.set_mode((dimension,dimension), pygame.RESIZABLE)
            self.width = int(open(field).readline().split()[0])
            cellsize = (dimension)//(self.width+2)
            size=cellsize*self.width
            self.fieldrect = pygame.Rect(0,0,size,size)
            self.fieldrect.x+=10
            self.fieldrect.y+=10
            self.field = SudokuField.from_file(field, pygame.Surface((size, size)), cellsize)
            self.selector = SudokuNumberSelector(len(self.field.field), pygame.Surface((size+cellsize,cellsize)), cellsize)
            self.selectorrect = self.selector.surface.get_rect()
            self.selectorrect.y = size+16+10
            self.selectorrect.x+=10
            self.score = SudokuScoreCounter(self.field, pygame.Surface((300, 30)))
            self.scorerect = self.score.surface.get_rect()
            self.scorerect.y+=self.selectorrect.y+self.selectorrect.height+5
            self.scorerect.x+=self.selectorrect.x
            self.ticks = 0
            self.update=False
            self.target=(800,600)
            #pygame.display.toggle_fullscreen()


            self.clock = pygame.time.Clock()
            #self.listen_click_thread = threading.Thread(target=self.listen_click, daemon=True)
            #self.listen_click_thread.start()
            self.listen_click()
        except:
            self.draw_error(traceback.format_exc())
    @staticmethod
    def get_path():
        a = tkinter.Tk()
        w = tkinter.Label(a, text="Select file in dialog (may be minimized)", font=("Helvetica", 24))
        w.pack()
        file=None
        while not file or file=='':
            file = tkinter.filedialog.askopenfilename()
        a.destroy()
        return file

    def reset_rects(self, width, height):
        dimension = min(width, height)
        cellsize = (dimension)//(self.width+2)
        size=cellsize*self.width
        self.fieldrect = pygame.Rect(0,0,size,size)
        self.fieldrect.x+=10
        self.fieldrect.y+=10
        self.field.surface = pygame.Surface((size, size))
        self.field.cellsize = cellsize
        self.field.recreate_cache()
        self.selector.surface = pygame.Surface((size+cellsize,cellsize))
        self.selector.cellsize = cellsize
        self.selector.reset_cache()
        self.selectorrect = self.selector.surface.get_rect()
        self.selectorrect.y = size+16+10
        self.selectorrect.x+=10
        self.scorerect = self.score.surface.get_rect()
        self.scorerect.y+=self.selectorrect.y+self.selectorrect.height+5
        self.scorerect.x+=self.selectorrect.x
        self.update = True
        self.ticks=0
        self.target=(width, height)



    def listen_click(self):
        while self.running:
            self.clock.tick(20)
            if self.update:
                print(self.ticks)
                self.ticks+=1
                if self.ticks>5:
                    self.ticks=0
                    self.update=False
                    self.surface = pygame.display.set_mode(self.target, pygame.RESIZABLE)
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key in [eval('pygame.K_'+i) for i in ['q','e', 'RETURN', 'ESCAPE', 'DELETE']]:
                        pygame.quit()
                        return None
                if event.type == pygame.VIDEORESIZE:
                    self.reset_rects(*event.size)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = event.pos
                    if self.fieldrect.collidepoint((x,y)):
                        self.field.select(x-self.fieldrect.x, y-self.fieldrect.y)
                    elif self.scorerect.collidepoint((x,y)):
                        self.score.click(x-self.scorerect.x, y-self.scorerect.y)
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
        self.score.draw()
        self.surface.blit(self.field.surface, self.fieldrect)
        self.surface.blit(self.selector.surface, self.selectorrect)
        self.surface.blit(self.score.surface, self.scorerect)
        pygame.draw.rect(self.surface, pygame.Color('white'), self.fieldrect, 3)
        pygame.draw.rect(self.surface, pygame.Color('white'), self.selectorrect, 3)
        pygame.display.update()

    @staticmethod
    def draw_error(error):
        error=['Unhandled exception!']+error.split('\n')+['Please report this.']
        font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        error = [font.render(str(i), True, pygame.Color('red')) for i in error]
        display = pygame.display.set_mode((max(error, key=lambda x: x.get_width()).get_width(), 32*(len(error)+1)))
        for i,j in enumerate(error):
            display.blit(j, (0, 32*i))
        pygame.display.flip()
        c=pygame.time.Clock()
        while 1:
            c.tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

if __name__ == '__main__':
    width=1920
    height=600
    game = SudokuGame(width, height)
    #input()
