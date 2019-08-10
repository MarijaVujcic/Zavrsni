from panda3d.core import loadPrcFile
if __debug__:
    loadPrcFile("Configuration/configuration.prc")
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class ShootEm(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

    def loadMainSpaceship(self):



app = ShootEm()
app.run()