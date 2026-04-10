# Group#: B50
# Student Names: Felipe Nunes and Nima Karimzadehshirazi

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"): 
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed) #game is a global variable representing the game object created in the main function below
            #whenAnArrowKeyIsPressed argument e is passed by the bind function and it contains the key that was pressed by the gamer. 
    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue: queue.Queue = gameQueue
        self.gui: Gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if DEBUG:
                    print(f"Handling task: {task}")
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point] #list of the snake coordinates in the form [x1, y1, x2, y2, ...] to be used in the canvas.coords method to update the snake icon coordinates
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            if DEBUG:
                print("Queue is empty, scheduling the next check")
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue: queue.Queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates: list[tuple[int, int]] = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction: str = "Left"
        self.gameNotOver: bool = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        if DEBUG:
            print("Starting superloop")
        while self.gameNotOver:
            #complete the method implementation below
            self.queue.put({"move": self.snakeCoordinates})
            time.sleep(SPEED)
            self.move() #move called here to make sure the snake coordinates are updated before the next move task is generated
            #this prevents a game over without the snake actually moving since the snake coordinates are not updated in the gui
            
    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        def isPreyCaptured(newSnakeCoordinates: tuple[int, int]) -> bool:
            """ 
                This helper method checks if the prey has been captured
                based on the new head coordinates of the snake.
                The prey is captured if the new head coordinates of the snake 
                are within the rectangle defined by the prey coordinates.
                Both the snake and the prey are represented as rectangles, so we need to check if the head of the snake (which is represented by a rectangle with the same coordinates as its center) is within the rectangle of the prey.
            """
            preyX1, preyY1, preyX2, preyY2 = self.preyCoordinates
            snakeX, snakeY = newSnakeCoordinates
            return (preyX1-SNAKE_ICON_WIDTH//2 <= snakeX <= preyX2 + SNAKE_ICON_WIDTH//2) and (preyY1-SNAKE_ICON_WIDTH//2 <= snakeY <= preyY2 + SNAKE_ICON_WIDTH//2)

        if DEBUG:
            print("Moving snake logic")
        NewSnakeCoordinates = self.calculateNewCoordinates()
        #complete the method implementation below
        self.snakeCoordinates.append(NewSnakeCoordinates) #appending new head coordinates to the snake coordinates list
        if isPreyCaptured(NewSnakeCoordinates): #checking if the prey has been captured
            if DEBUG:
                print("Prey captured!")
            self.score += 1
            self.queue.put({"score": self.score})
            #need to remove the prey from the canvas before creating a new one since the createNewPrey method only updates the prey coordinates and does not check if there is already a prey on the canvas
            self.queue.put({"prey": (0, 0, 0, 0)}) #removing the prey from the canvas by setting its coordinates to (0, 0, 0, 0)
            self.createNewPrey()
        else:
            self.snakeCoordinates.pop(0) #removing the tail coordinates from the snake coordinates list since the snake has not captured the prey and thus its length should not increase
        #edgecase: prey could be on snake coordinates, so we should check if the game is over outside of the if statement 
        self.isGameOver(NewSnakeCoordinates) #checking if the game is over based on the new head coordinates

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1] #getting the current head coordinates of the snake
        #complete the method implementation below
        if self.direction == "Left":
            return (lastX - SNAKE_ICON_MOVE_STEP, lastY) #left is associated with decreasing the x coordinate
        elif self.direction == "Right":
            return (lastX + SNAKE_ICON_MOVE_STEP, lastY) #right is associated with increasing the x coordinate
        elif self.direction == "Up":
            return (lastX, lastY - SNAKE_ICON_MOVE_STEP) #up is associated with decreasing the y coordinate
        elif self.direction == "Down":
            return (lastX, lastY + SNAKE_ICON_MOVE_STEP) #down is associated with increasing the y coordinate
        #no need to check for the direction validity since it is already checked in whenAnArrowKeyIsPressed method

    def isGameOver(self, snakeCoordinates: tuple[int, int]) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        #complete the method implementation below

        #Wall collision is checked using the head CENTER coordinate, since
        #snakeCoordinates stores center points for the Tkinter line. This means the
        #visible thick snake may appear to touch or slightly cross a wall before the
        #game ends. To make collision depend on the visible edge instead, half of
        #SNAKE_ICON_WIDTH would need to be included in the boundary check.
        if (x < 0 or x >= WINDOW_WIDTH or y < 0 or y >= WINDOW_HEIGHT or self.snakeCoordinates.count(snakeCoordinates) > 1):
            #we actually need to check if there are two instances of the new head coordinates in the snake coordinates 
            #list since the new head coordinates are already appended to the snake coordinates list before calling this method
            self.gameNotOver = False
            self.queue.put({"game_over": True})

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        #new prey coordinates can be placed on top of the snake!
        THRESHOLD = 15   #sets how close prey can be to borders
        #complete the method implementation below
        x = random.randint(THRESHOLD + PREY_ICON_WIDTH_HALF, WINDOW_WIDTH - THRESHOLD - PREY_ICON_WIDTH_HALF) #randomly picking x coordinate for the centre of prey
        y = random.randint(THRESHOLD + PREY_ICON_WIDTH_HALF, WINDOW_HEIGHT - THRESHOLD - PREY_ICON_WIDTH_HALF) #randomly picking y coordinate for the centre of prey
        #must include the PREY_ICON_WIDTH_HALF in the random range to make sure the prey is fully visible and not partially out of bounds
        self.preyCoordinates = (x - PREY_ICON_WIDTH_HALF, y - PREY_ICON_WIDTH_HALF, x + PREY_ICON_WIDTH_HALF, y + PREY_ICON_WIDTH_HALF) #calculating the prey rectangle coordinates based on the prey center coordinates and the prey icon width
        self.queue.put({"prey": self.preyCoordinates})

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500          
    WINDOW_HEIGHT = 500 
    SNAKE_ICON_WIDTH = 10
    SNAKE_ICON_MOVE_STEP = 10 #this is based on the starting coordinates of the snake specified above 
    SNAKE_ICON_WIDTH_HALF = SNAKE_ICON_WIDTH // 2 #half of the snake icon width 
    # Important Note: Since the snake moves in steps of SNAKE_ICON_MOVE_STEP, whether 
    # it appears to reach a wall depends on both the window size and the initial coordinates.
    # Even if the window dimensions are divisible by SNAKE_ICON_WIDTH, the snake
    # may still seem to stop early if its starting position is not aligned so that
    # repeated step-sized moves land exactly on the window boundary.

    #add the specified constant PREY_ICON_WIDTH here     
    PREY_ICON_WIDTH = 10
    PREY_ICON_WIDTH_HALF = PREY_ICON_WIDTH // 2 #half of the prey icon width 

    BACKGROUND_COLOUR = "grey"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    DEBUG = False                   #set to True to enable debug output

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()
