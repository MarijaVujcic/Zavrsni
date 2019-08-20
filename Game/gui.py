""" simple method and hints to set dgui elements according
to the windows aspect ratio """

import sys
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectLabel
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode


class Sample(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # create a main frame as big as the window
        self.frameMain = DirectFrame(
            frameSize=(base.a2dLeft, base.a2dRight,
                       base.a2dTop, base.a2dBottom),
            # position center
            pos=(0, 0, 0),
            # set tramsparent background color
            frameColor=(0, 0, 0, 0))
        # create a sample title
        self.textscale = 0.15
        self.title = DirectLabel(
            scale=self.textscale,
            pos=(0.0, 0.0, base.a2dTop - self.textscale),
            frameColor=(0, 0, 0, 0),
            text="aspect ratio sample",
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1))
        self.title.setTransparency(1)
        self.title.reparentTo(self.frameMain)

        # create a sample exit button
        self.btnExit = DirectButton(
            scale=(0.25, 0.25, 0.25),
            text="Exit",
            # position on the window
            pos=(-1, 0, .55),
            # the event which is thrown on clickSound
            command=lambda: sys.exit(),
            # sounds that should be played
            rolloverSound=None,
            clickSound=None)
        self.btnExit.setTransparency(1)
        self.btnExit.reparentTo(self.frameMain)

        # catch window resizes and recalculate the aspectration
        self.accept('window-event', self.recalcAspectRatio)

    def recalcAspectRatio(self, window):
        """get the new aspect ratio to resize the mainframe"""
        # set the mainframe size to the window borders again
        self.frameMain["frameSize"] = (
            base.a2dLeft, base.a2dRight,
            base.a2dTop, base.a2dBottom)

        # calculate new aspec tratio
        wp = window.getProperties()
        aspX = 1.0
        aspY = 1.0
        wpXSize = wp.getXSize()
        wpYSize = wp.getYSize()
        if wpXSize > wpYSize:
            aspX = wpXSize / float(wpYSize)
        else:
            aspY = wpYSize / float(wpXSize)
        # calculate new position/size/whatever of the gui items
        self.btnExit.setPos(-1 * aspX + 0.25, 0, .55 * aspY)
        self.title.setPos(0.0, 0.0, base.a2dTop - self.textscale)


s = Sample()
s.run()
