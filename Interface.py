import sys
import os.path


def render():
    run = True
    while run:
        message = input('Would you like to enable rendering? (y/n) ')
        if message == 'y' or message == 'Y':
            result = True
            run = False
        elif message == 'n' or message == 'N':
            result = False
            run = False
        else:
            print('input not understood.  Please use y or Y for yes and n or N for no ')
    return result


def resume():
    run = True
    while run:
        message = input('Would you like to resume from a previous checkpoint? (y/n) ')
        if message == 'y' or message == 'Y':
            result = True
            run = False
        elif message == 'n' or message == 'N':
            result = False
            run = False
        else:
            print('input not understood.  Please use y or Y for yes and n or N for no ')
    return result


def askForResumeName():
    run = True
    while run:
        message = input('You have indicated that you wish to resume from a previous checkpoint.\nWhat is the name of '
                        'the file to resume from? (please include .p file extension in your input) ')
        if not fileExists(message):
            print('The file {} does not exists, please try again.'.format(message))
        else:
            run = False
    return message


def askForNewName():
    message = input('You are about to start with a new model.\nWhat would you like to name it? (please include .p '
                    'file extension in your input) ')
    run = True
    while fileExists(message) and run:
        m2 = input('A file already exists under this name ({}).  Are you sure you wish to overwrite this file? (y to '
                   'continue or n to input a new filename) '.format(message))
        if m2 == 'y' or m2 == 'Y':
            run = False
        elif m2 == 'n' or m2 == 'N':
            message = input(
                'You are about to start with a new model.\nWhat would you like to name it? (please include .p '
                'file extension in your input) ')
        else:
            print('input not understood.  Please use y or Y for yes and n or N for no ')
    return message


def fileExists(name):
    if os.path.exists(name):
        return True
    else:
        return False


def dataCollection():
    run = True
    while run:
        message = input('Would you like to enable collection of reward sum and running reward mean? (y/n) ')
        if message == 'y' or message == 'Y':
            result = True
            run = False
        elif message == 'n' or message == 'N':
            result = False
            run = False
        else:
            print('input not understood.  Please use y or Y for yes and n or N for no ')
    return result


def dcFilename():
    message = input('Please enter the name of the file you would like to have the data written to ')
    run = True
    while fileExists(message) and run:
        m2 = input('A file already exists under this name ({}).  Are you sure you wish to overwrite this file? (y to '
                   'continue or n to input a new filename) '.format(message))
        if m2 == 'y' or m2 == 'Y':
            run = False
        elif m2 == 'n' or m2 == 'N':
            message = input('Please enter the name of the file you would like to have the data written to ')
        else:
            print('input not understood.  Please use y or Y for yes and n or N for no ')
    return message


def changeParams(current_params):
    names = ['# of hidden nodes', 'Batch size', 'Learning rate', 'Discount factor', 'Decay rate']
    run = True
    while run:
        message = input(
            'The current hyper parameters are as follows:\n1. {}: {}\n2. {}: {}\n3. {}: {}\n4. {}: {}\n5. {}: {}\n'
            'Type the number next to the parameter you wish to change or 0 to continue. '.format(names[0],
            current_params[0], names[1], current_params[1], names[2], current_params[2], names[3], current_params[3], names[4], current_params[4]))
        if not (message.isdigit()):
            print('Input not a digit\n')
        else:
            mint = int(message)
            if mint not in range(len(names) + 1):
                print('Input not in range of given options\n')
            elif mint == 0:
                run = False
            else:
                current_params[mint-1] = updateParam(names[mint-1])
    return current_params

def updateParam(name):
    run = True
    while run:
        newVal = input('Please enter the new value for {}'.format(name))
        if not newVal.isdigit():
            print('new value must only contain digits (Hint: 1e-3 = 0.001)')
        else:
            run = False
    return newVal