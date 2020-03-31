##Math 198 final project
##Cameron Cuzmanko Fall 2015
##Use W,A,S,D for movement! W=up, A=left, S=down, D=down, Q=into the screen, E=out of the screen. Press escape to quit program
from vpython import *
from random import randint

##establishes what value the x,y, and z will have
positionNum = 20
##size of each side is twice the position
size = 2 * positionNum
rad = positionNum / 20

##velocity should be kept at <(1/20)*position because any higher and numerous problems may occur with bounces
##weird bounces will still occur occasionally regardless of velocity
xVelocity = .4  ##random.random()/4 for random number between 0.0 and 0.25
yVelocity = .4
zVelocity = .8

##creates the walls using the positions and size
xzBottomWall = box(pos=vector(0, -positionNum, 0), length=size, height=0.01, width=size, color=color.blue)
xzTopWall = box(pos=vector(0, positionNum, 0), length=size, height=0.01, width=size, color=color.blue)

yzRightWall = box(pos=vector(positionNum, 0, 0), length=.01, height=size, width=size, color=color.red)
yzLeftWall = box(pos=vector(-positionNum, 0, 0), length=.01, height=size, width=size, color=color.red)

##creates front wall as invisible wall so user can see inside
xyBackWall = box(pos=vector(0, 0, -positionNum), length=positionNum / 6, height=positionNum / 6, width=0.01,
                 color=color.green, opacity=1)
userPaddle = box(pos=vector(0, 0, positionNum), length=positionNum / 6, height=positionNum / 6, width=0.01,
                 color=color.yellow, opacity=1)

##creates ball and establishes velocity
ball = sphere(pos=vector(0, 0, 0), radius=rad, color=color.green)
ball.velocity = vector(xVelocity, yVelocity, zVelocity)
ball.visible = False

start_text = text(text='Click to \nBegin', align='center', depth=-.3, color=color.green, pos=vector(0, 0, 25), height=5, width=3)
win_text = text(text='You Won!! \nR to replay \nEsc to Quit', align='center', depth=-.3, color=color.green, pos=vector(0, 0, 25), height=5, width=3)
win_text.visible = False
loose_text = text(text='You Lost \nR to replay \nEsc to Quit', align='center', depth=-.3, color=color.green, pos=vector(0, 0, 25), height=5, width=3)
loose_text.visible = False
ev = scene.waitfor('click')

run = True

# def handleKey( evt ):
# print(evt.key)

def move(s):
    if len(s) > 1:
        print('greater than 1')
    for key in s:
        if key == 'd':
            if userPaddle.pos.x < yzRightWall.pos.x - (userPaddle.length / 2):
                userPaddle.pos.x += 1
        if key == 's':
            if userPaddle.pos.y > xzBottomWall.pos.y + (userPaddle.height / 2):
                userPaddle.pos.y -= 1
        if key == 'a':
            if userPaddle.pos.x > yzLeftWall.pos.x + (userPaddle.length / 2):
                userPaddle.pos.x -= 1
        if key == 'w':
            if userPaddle.pos.y < xzTopWall.pos.y - (userPaddle.length / 2):
                userPaddle.pos.y += 1
        if key == 'e':
            if userPaddle.pos.z < positionNum:
                userPaddle.pos.z += .5
        if key == 'q':
            if userPaddle.pos.z > positionNum - 5:
                userPaddle.pos.z -= .5
        # escape to end
        if key == "esc":
            quit()
            scene.delete()


def collide(dir):
    if dir == 'x':
        ball.velocity.x = -ball.velocity.x
    if dir == 'y':
        ball.velocity.y = -ball.velocity.y
    if dir == 'z':
        ball.velocity.z = -(1.05) * ball.velocity.z
        print(ball.velocity.x)
        print(ball.velocity.y)
        print(ball.velocity.z)


def moveAI():
    if ball.pos.x > xyBackWall.pos.x:
        xyBackWall.pos.x += .22
    if ball.pos.x < xyBackWall.pos.x:
        xyBackWall.pos.x -= .22
    if ball.pos.y > xyBackWall.pos.y:
        xyBackWall.pos.y += .22
    if ball.pos.y < xyBackWall.pos.y:
        xyBackWall.pos.y -= .22


def replay(keys):
    for key in keys:
        if key == 'r':
            break
        if key == 'esc':
            run = False


def win_Con():
    ball.visible = False
    win_text.visible = True
    input = keysdown()
    replay(input)
    loose_text.visible = False


def loose_Con():
    ball.visible = False
    loose_text.visible = True
    input = list()
    while len(input) == 0:
        input =  keysdown()
    replay(input)
    loose_text.visible = False

userTurnToHit = True

while run:
    start_text.visible = True
    ball.pos = vector(0,0,0)
    if ev.event == 'click':
        start_text.visible = False
        ball.visible = True
        while True:
            ##halts computations briefly
            rate(10)
            ##changes ball position by adding velocity to position
            ##this is why a big velocity causes problems, makes position beyond borders
            ball.pos = ball.pos + ball.velocity
            ##conditionals check to see if the ball's x,y or z position is beyond the wall
            ##if one of them is, it flips that component of the velocity
            if ball.pos.y - ball.radius < -positionNum:
                collide('y')
            if ball.pos.y + ball.radius > positionNum:
                collide('y')
            if ball.pos.x - ball.radius < -positionNum:
                collide('x')
            if ball.pos.x + ball.radius > positionNum:
                collide('x')
            if ball.pos.x - ball.radius < userPaddle.pos.x + userPaddle.length / 2 and ball.pos.x + ball.radius > userPaddle.pos.x - userPaddle.length / 2 and ball.pos.y - ball.radius < userPaddle.pos.y + userPaddle.length / 2 and ball.pos.y + ball.radius > userPaddle.pos.y - userPaddle.length / 2 and ball.pos.z + ball.radius > userPaddle.pos.z and userTurnToHit:
                if ball.pos.x > userPaddle.pos.x + userPaddle.length / 4 or ball.pos.x < userPaddle.pos.x - userPaddle.length / 4:
                    ball.velocity.x = (1.05) * ball.velocity.x
                if ball.pos.y > userPaddle.pos.y + userPaddle.height / 4 or ball.pos.y < userPaddle.pos.y - userPaddle.length / 4:
                    ball.velocity.y = (1.05) * ball.velocity.y
                collide('z')
                userTurnToHit = False
            if ball.pos.x - ball.radius < xyBackWall.pos.x + xyBackWall.length / 2 and ball.pos.x + ball.radius > xyBackWall.pos.x - xyBackWall.length / 2 and ball.pos.y - ball.radius < xyBackWall.pos.y + xyBackWall.length / 2 and ball.pos.y + ball.radius > xyBackWall.pos.y - xyBackWall.length / 2 and ball.pos.z - ball.radius < xyBackWall.pos.z and not userTurnToHit:
                if ball.pos.x > xyBackWall.pos.x + xyBackWall.length / 4 or ball.pos.x < xyBackWall.pos.x - xyBackWall.length / 4:
                    ball.velocity.x = (1.05) * ball.velocity.x
                if ball.pos.y > xyBackWall.pos.y + xyBackWall.height / 4 or ball.pos.y < xyBackWall.pos.y - xyBackWall.length / 4:
                    ball.velocity.y = (1.05) * ball.velocity.y
                collide('z')
                userTurnToHit = True
            if ball.pos.z - ball.radius < -positionNum - 2 * ball.radius:
                # win
                win_Con()
                break
            if ball.pos.z + ball.radius > positionNum + 2 * ball.radius:
                # lose
                loose_Con()
                break
            ##very basic implementation of final AI
            ##will attempt to fix lag and ability of AI later on
            moveAI()
            keyPressed = keysdown()
            if len(keyPressed) is not 0:
                move(keyPressed)
