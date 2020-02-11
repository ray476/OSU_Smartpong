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
    message = input('You have indicated that you wish to resume from a previous checkpoint.\nWhat is the name of the '
                    'file to resume from? (please include .p file extension in your input) ')
    if not fileExists(message):
        print('The file {} does not exists, a new model will be created under that name'.format(message))
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





