import sys, random
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QIcon
from functools import reduce
class Tetro(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()

        
    def initUI(self):    

        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)
 
        self.statusbar = self.statusBar()        
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.setWindowIcon(QIcon('image.jpg'))
        self.tboard.start()
        
        self.resize(360, 380)
        self.center()
        self.setWindowTitle('Tetramino')
        self.show()
        
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, 
            (screen.height()-size.height())/2)
        
class Board(QFrame):
    step=0
    msg2Statusbar = pyqtSignal(str)
    BoardWidth = 8
    BoardHeight = 8
    Speed = 300 # del

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):     
        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False

    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]
 
    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape
        
    def squareWidth(self):
        return self.contentsRect().width() // Board.BoardWidth
        
    def squareHeight(self):
        return self.contentsRect().height() // Board.BoardHeight
    def initGame(self):
        Board.step = 0
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.clearBoard()

        self.teams=[ [x for x in range(0,8)], [0]+[x for x in range(7,0,-1)]]
        self.dictSymbol = {i: x for i, x in enumerate([0, 'Z', 'S', 'I', 'T', '[]', 'L', 'J'])}
        return
    def start(self):
        if self.isPaused:
            return
        self.initGame()
        self.isStarted = True
 
        self.msg2Statusbar.emit(str(self.numLinesRemoved))
 
        self.newPiece()
        self.timer.start(Board.Speed, self)
 
    def pause(self):
        
        if not self.isStarted:
            return
        self.isPaused = not self.isPaused
        
        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")
        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()
 
        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()
 
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                
                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                        rect.left() + j * self.squareWidth(),
                        boardTop + i * self.squareHeight(), shape)
 
        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                    self.curPiece.shape())
 
    def keyPressEvent(self, event):
        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return
 
        key = event.key()
        
        if key == Qt.Key_P:
            self.pause()
            return
        if self.isPaused:
            return
                
        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece, self.curX, self.curY-1)
        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece, self.curX, self.curY+1)

        elif key == Qt.Key_D:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
        elif key == Qt.Key_A:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
        elif key == Qt.Key_S:
            self.nextPiece()
        elif key == Qt.Key_W:
            if self.tryMove2(self.curPiece, self.curX, self.curY):    #перекрытие
                self.pieceDropped()
        elif key == Qt.Key_N:  
            self.start()

        else:
            super(Board, self).keyPressEvent(event)

    def clearBoard(self):
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

            
    def pieceDropped(self):
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())
        self.teams[Board.step%2].pop(self.teams[Board.step%2].index(self.curPiece.shape()))

        self.newPiece()
            

    def newPiece(self):
        if len(self.teams[Board.step%2])<=1:
#            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Выиграл "+str(1 if Board.step%2 else 2)+'й игрок')
            return
        Board.step+=1
        self.getGameStr()
        if Board.step>9:
            if not self.checkWinner():
                #self.isStarted = False
                self.msg2Statusbar.emit("Выиграл " + str(Board.step % 2 +1) + 'й игрок')


        self.curPiece = Shape()
        self.curPiece.setShape(self.teams[Board.step%2][1])
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
        return

    def getSymbolTeam(self, numTeam):
        return reduce(lambda x,y: x+y, map(lambda x: self.dictSymbol[x] , self.teams[numTeam][1:] ) )

    def getGameStr(self,comment='', add=False):
        comment=str(comment)
        if not add:
            self.msg2Statusbar.emit(str(Board.step) + '  1ый: ' + self.getSymbolTeam(1) +
                    ' , 2ой: ' + self.getSymbolTeam(0) + '  ход '+str((Board.step+1)%2+1)+'ого ' + comment)
        else:
            self.msg2Statusbar.emit(comment)
        return

    def nextPiece(self):
        self.curPiece.nextRandomShape(self.teams[Board.step%2])
        self.getGameStr()

    def checkWinner(self):
        curPiece = Shape()
        for shape in self.teams[(Board.step) % 2][1:]:
            curPiece.setShape(shape)
            for k in range(4):
                curPiece.rotateRight()
                for i, a in enumerate(self.board):
                    if not a:
                        if self.checkTryMove(curPiece, i % 8, i // 8):
                            return True
        return False

    def checkTryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False
        return True
    def tryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()
        return True

    def tryMove2(self, newPiece, newX, newY):
        if not self.checkTryMove(newPiece, newX, newY):
            return False
        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()
        return True
        
    def drawSquare(self, painter, x, y, shape):                
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,            
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
            self.squareHeight() - 2, color)
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)
 
        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1, 
            y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)
class Tetrominoe(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7
class Shape(object):
    
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )
 
    def __init__(self):
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        self.setShape(Tetrominoe.NoShape)
        
    def shape(self):
        return self.pieceShape
 
    def setShape(self, shape):
        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
 
        self.pieceShape = shape
        
    def setRandomShape(self):
        self.setShape(random.randint(1, 7))

    def nextRandomShape(self,team):
        k=(team.index(self.shape())+1)%len(team)
        if k==0:
            k=1
        self.setShape(team[k])
 
    def x(self, index):
        return self.coords[index][0]
   
    def y(self, index):
        return self.coords[index][1]
 
    def setX(self, index, x):
        self.coords[index][0] = x
 
    def setY(self, index, y):
        self.coords[index][1] = y
 
    def minX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
 
        return m
 
    def maxX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
 
        return m
 
    def minY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
 
        return m
 
    def maxY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])
 
        return m
 
    def rotateLeft(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
 
        result = Shape()
        result.pieceShape = self.pieceShape
        
        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))
 
        return result

    def rotateRight(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
 
        result = Shape()
        result.pieceShape = self.pieceShape
        
        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))
 
        return result
 
if __name__ == '__main__':
    app = QApplication([])
    tetro = Tetro()
    sys.exit(app.exec_())
