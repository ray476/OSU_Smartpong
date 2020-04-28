import sys
import os.path
import numpy as np
import Database

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


def askForResumeName(DBconnection):
    run = True
    while run:
        message = input('You have indicated that you wish to resume from a previous checkpoint.\nPlease select a name from the list below  ' )
        Database.showModels(DBconnection)
        run = False

    return message
        # if not fileExists(message):
        #     print('The file {} does not exists, please try again.'.format(message))



def askForNewName():
    message = input('You are about to start with a new model.\nWhat would you like to name it? ')
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
    message = input('\nPlease enter the name of the file you would like to have the data written to ')
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
    print('\n')
    return message


def changeParams(current_params):
    names = ['# of hidden nodes', 'Batch size', 'Learning rate', 'Discount factor', 'Decay rate']
    run = True
    while run:
        message = input(
            '\nThe default hyper parameters are as follows:\n1. {}: {}\n2. {}: {}\n3. {}: {}\n4. {}: {}\n5. {}: {}\n'
            'You will not be change them once the model is created\nType the number next to the parameter you wish to '
            'change or 0 to continue. '.format(names[0], current_params[0], names[1], current_params[1], names[2], current_params[2], names[3], current_params[3], names[4], current_params[4]))
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


def showParams(current_params):
    names = ['# of hidden nodes', 'Batch size', 'Learning rate', 'Discount factor', 'Decay rate']
    print('\nThe hyper parameters associated with this model are:\n1. {}: {}\n2. {}: {}\n3. {}: {}\n4. {}: {}\n5. {}: {}\n'.
          format(names[0],current_params[0], names[1], current_params[1], names[2], current_params[2], names[3], current_params[3], names[4], current_params[4]))


def updateParam(name):
    run = True
    while run:
        newVal = input('Please enter the new value for {} '.format(name))
        if not newVal.isdigit():
            print('new value must only contain digits (Hint: 1e-3 = 0.001)')
        else:
            run = False
    return newVal


# takes the current data collection and updates the episode numbers and running mean to include an older data collection
# file.  Currently, only writes these values to the old file, the current file is left untouched
# N.B. in the arrays of the text files, 0 is the episode number, 1 is reward sum for that episode and 2 is the mean
def mergeFiles(fileobject, old_file):
    # open the previous file
    original_file = open(old_file, 'r+')
    original_array = np.loadtxt(original_file)
    # get the last episode and last mean, episode starts at 0, so increment by 1 or the last_episode_num will be
    # duplicated
    last_episode_num = original_array[-1][0] + 1
    last_mean = original_array[-1][2]
    # close the file as it is in write mode and the buffer is at the end of the file, re-open in read mode at the head
    # of the file
    new_file_name = fileobject.name
    fileobject.close()
    new_file = open(new_file_name, 'r')
    # convert the file to be appended to an array
    new_array = np.loadtxt(new_file)
    new_file.close()

    # add the last episode number from the previous run to every episode number in the new file
    for i in range(new_array.shape[0]):
        new_array[i][0] += last_episode_num

# it looks like the 'running mean' in the current program is calculated with "running_reward * 0.99 + reward_sum * 0.01"
# not sure if this is really a mean, come back to this later, but for now use it to stay consistent

    new_array[0][2] = (last_mean * 0.99) + (new_array[0][1] * 0.01)
    for i in range(1, new_array.shape[0]):
        new_array[i][2] = (new_array[i-1][2] * 0.99) + (new_array[i][1] * 0.01)

    # https://math.stackexchange.com/questions/22348/how-to-add-and-subtract-values-from-an-average
    # now to update the running mean, do the first value with the mean from the old file, then loop starting at 1
    # new_array[0][2] = last_mean + ((new_array[0][1] - last_mean) / new_array[0][0])
    # for i in range(1, new_array.shape[0]):
        # new_array[i][2] = new_array[i-1][2] + ((new_array[i][1] - new_array[i-1][2]) / new_array[i][0])

    # now to append the updated new array values to the old file
    for i in range(new_array.shape[0]):
        original_file.write('{} {} {}\n'.format(int(new_array[i][0]), int(new_array[i][1]), new_array[i][2]))

    original_file.close()


def mergeFilesNoMean(fileobject, old_file):
    # open the previous file
    original_file = open(old_file, 'r+')
    original_array = np.loadtxt(original_file)
    # get the last episode and last mean, episode starts at 0, so increment by 1 or the last_episode_num will be
    # duplicated
    last_episode_num = int(original_array[-1][0] + 1)
    # close the file as it is in write mode and the buffer is at the end of the file, re-open in read mode at the head
    # of the file
    new_file_name = fileobject.name
    fileobject.close()
    new_file = open(new_file_name, 'r')
    # convert the file to be appended to an array
    new_array = np.loadtxt(new_file)
    new_file.close()

    # add the last episode number from the previous run to every episode number in the new file
    for i in range(new_array.shape[0]):
        new_array[i][0] += last_episode_num

# it looks like the 'running mean' in the current program is calculated with "running_reward * 0.99 + reward_sum * 0.01"
# not sure if this is really a mean, come back to this later, but for now use it to stay consistent


    # https://math.stackexchange.com/questions/22348/how-to-add-and-subtract-values-from-an-average
    # now to update the running mean, do the first value with the mean from the old file, then loop starting at 1
    # new_array[0][2] = last_mean + ((new_array[0][1] - last_mean) / new_array[0][0])
    # for i in range(1, new_array.shape[0]):
        # new_array[i][2] = new_array[i-1][2] + ((new_array[i][1] - new_array[i-1][2]) / new_array[i][0])

    # now to append the updated new array values to the old file
    for i in range(new_array.shape[0]):
        original_file.write('{} {}\n'.format(int(new_array[i][0]), int(new_array[i][1])))

    original_file.close()