from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

import random
import os
#from pip._vendor.distlib.compat import raw_input

class Field(object):
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def cells(self):
        for x in range(self.height):
            for y in range(self.width):
                yield x,y
                
    def empty(self):
        self.field=dict()
        for xy in self.cells():
                self.field[xy]='e'
        
    def show(self, transform):
        print('   ', end='')
        for x in range(self.width):
            print( "%s  " % chr( x + ord('a')), end='')
        print()
        for y in range(self.height):
            print( "%2d " % (y+1), end='' )
            for x in range(self.width):
                print(transform(self.field[(x,y)]), ' ', end='')
            print()
        print()
    
    def reveal(self):
        self.show( lambda x: x )

    def display(self):
        self.show( lambda x: '*' if x in ['e', 'M'] else 'F' if x[0]=='F' else x )
        
    def layMines(self, numMines):
        for m in range(numMines):
            while True:
                xy = int(random.random()*self.width), int(random.random()*self.height)
                if self.field[xy] == 'M':
                    continue
                self.field[xy] = 'M'
                break

    def neighbours(self,xy):
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx==0 and dy==0:
                    continue
                x1,y1 = xy[0]+dx, xy[1]+dy
                if 0 <= x1 <= self.width-1 and 0 <= y1 <= self.height-1:
                    yield x1,y1
        
    def minesAround(self,xy):
        count = 0
        for xy1 in self.neighbours(xy):
            if self.field[xy1] in ['M', 'FM']:
                count += 1 
        return count
        
    def expose(self):
        again=True
        while again:
            again=False
            for xy in self.cells():
                if self.field[xy] == '0':
                    again=True
                    self.field[xy] = '.'
                    for xy1 in self.neighbours(xy):
                        if self.field[xy1] == 'e':
                            self.field[xy1] = str(self.minesAround(xy1))
        
    def step(self,xy):
        if self.field[xy] == 'M':
            self.field[xy] = 'B'
            return
        self.field[xy] = str(self.minesAround(xy))
        self.expose()
        
    def flag(self,xy):
        if self.field[xy][0] == 'F':
            self.field[xy] = self.field[xy][1:]
        else:
            self.field[xy] = 'F' + self.field[xy]

class Game(object):
    
    def __init__(self):
        self.field = Field(10,10)
        self.field.empty()
        self.minesLeft = 15
        self.field.layMines(self.minesLeft)
        self.status = 'ready'

    def display(self):
        print( 'status: ', self.status )
        print( 'mines left: ', self.minesLeft )
        self.field.reveal()
        self.field.display()
        
    def step(self,x,y):
        if self.status=='game over':
            print('game over')
            return
        if self.field.field[ (x,y) ] == 'M':
            print('boom!')
            self.display()
            self.status='game over'
            return
        self.field.step( (x,y) )
        self.display()

    def flag(self,x,y):
        self.field.flag( (x,y) )
        self.display()


g = Game()

@app.route('/')
def game_default():
    global g
    return render_template('game.html', game=g )

@app.route('/new_game')
def game_new():
    global g
    g = Game()
    return render_template('game.html', game=g )

@app.route('/step/<x>/<y>')
def game_step(x,y):
    g.step(int(x),int(y))
    return render_template('game.html', game=g)

@app.route('/flag/<x>/<y>')
def game_flag(x,y):
    g.flag(int(x),int(y))
    return render_template('game.html', game=g)

@app.route('/quit_server')
def quit_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Quitting..."
   
port = int(os.getenv("PORT"))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port) 
