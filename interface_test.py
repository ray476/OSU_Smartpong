import Interface

print(Interface.render())
# y at first
resume = Interface.resume()
print(resume)
if resume:
    name = Interface.askForResumeName()
    print(name)
else:
    print('test failed')
# enter n now
resume = Interface.resume()
if not resume:
    name = Interface.askForNewName()
    print(name)
else:
    print('test failed')
