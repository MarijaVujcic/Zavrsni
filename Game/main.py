
from direct.showbase.ShowBase import ShowBase, Vec4
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.bullet import BulletWorld
from panda3d.core import Vec3, NodePath, PandaNode, AmbientLight, DirectionalLight

import sys
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectLabel
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.startGui()
    def startGui(self):
        self.frameMain = DirectFrame(
            frameSize=(base.a2dLeft, base.a2dRight,
                       base.a2dTop, base.a2dBottom),
            pos=(0, 0, 0),
            frameColor=(0, 0, 0, 0))
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
        self.btnStart = DirectButton(
            scale=(0.25, 0.25, 0.25),
            text="Start",
            # position on the window
            pos=(-1, 0, .55),
            command=lambda: self.gameStart(),
            rolloverSound=None,
            clickSound=None)
        self.btnStart.setTransparency(1)
        self.btnStart.reparentTo(self.frameMain)
        self.btnExit = DirectButton(scale=(0.25, 0.25, 0.25),
            text="Exit",
            # position on the window
            pos=(0, 0, .40),
            command=lambda: sys.exit(),
            rolloverSound=None,
            clickSound=None)
        self.btnExit.setTransparency(1)
        self.btnExit.reparentTo(self.frameMain)


    def gameStart(self):
            self.frameMain.destroy()  ##unisti gui
            self.keyMap = {"left": 0, "right": 0, "forward": 0, "up": 0, "backward":0, "down": 0, "center": 0}

            self.skysphere = self.loader.loadModel("SkySphere.bam")
            self.skysphere.setBin('background', 1)
            self.skysphere.setDepthWrite(0)
            self.skysphere.reparentTo(self.render)

            self.spaceship = self.loader.loadModel("Assets/Characters/spaceship.egg")
            self.spaceship.reparent_to(self.render)
            self.spaceship.setScale(.2)


            self.spaceship.setPos(Vec3(-110.9, 29.4, 1.8))

            #nesto sto će pratit spaceship
            self.itfollows= NodePath(PandaNode("itfollows"))
            self.itfollows.reparent_to(self.render)

            self.accept("escape", sys.exit)
            self.accept("arrow_left", self.setKey, ["left", 1])
            self.accept("arrow_right", self.setKey, ["right", 1])
            self.accept("arrow_up", self.setKey, ["forward", 1])
            self.accept("arrow_down", self.setKey, ["backward", 1])
            self.accept("arrow_left-up", self.setKey, ["left", 0])
            self.accept("arrow_right-up", self.setKey, ["right", 0])
            self.accept("arrow_up-up", self.setKey, ["forward", 0])
            self.accept("arrow_down-up", self.setKey, ["backward", 0])

            self.accept("w", self.setKey, ["up", 1])
            self.accept("w-up", self.setKey, ["up", 0])
            self.accept("s", self.setKey, ["down", 1])
            self.accept("s-up", self.setKey, ["down", 0])
            self.accept("q", self.setKey, ["center", 1])
            self.accept("q-up", self.setKey, ["center", 0])
            self.taskMgr.add(self.move, "moveTask")


            #lightning
            ambientLight = AmbientLight("ambientLight")
            ambientLight.setColor(Vec4(.3, .3, .3, 1))
            directionalLight = DirectionalLight("directionalLight")
            directionalLight.setDirection(Vec3(-5, -5, -5))
            directionalLight.setColor(Vec4(5, 4, 2, 0))
            directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
            self.render.setLight(self.render.attachNewNode(ambientLight))
            self.render.setLight(self.render.attachNewNode(directionalLight))
            #
            # Physics
            #
            self.world = BulletWorld()
            self.world.setGravity(Vec3(0, 0, -9.81))
            self.taskMgr.add(self.update, 'camera-physics-update')

            #
            # Camera
            #
            self.acceptOnce("+", self.zoom, [True])
            self.acceptOnce("-", self.zoom, [False])
            self.disableMouse()
            self.camera.setPos(self.spaceship.getX() + 10, self.spaceship.getY() + 10, 2)
            self.camLens.setFov(80)

            # this variable will set an offset to the node the cam is attached to
            # and the point the camera looks at. By default the camera will look
            # directly at the node it is attached to
            self.lookatOffset = Vec3(self.spaceship.getX(),self.spaceship.getY(), self.spaceship.getZ())
            # the next two vars will set the min and max distance the cam can have
            # to the node it is attached to
            self.maxCamDistance = 25
            self.minCamDistance = 25
            # the initial cam distance
            self.camDistance = (self.maxCamDistance - self.minCamDistance) / 2.0 + self.minCamDistance
            # the next two vars set the min and max distance on the Z-Axis to the
            # node the cam is attached to
            self.maxCamHeightDist = 25
            self.minCamHeightDist = 25
            # the average camera height
            self.camHeightAvg = (self.maxCamHeightDist - self.minCamHeightDist) / 2.0 + self.minCamHeightDist
            # the average camera height
            self.camHeightAvg = (self.maxCamHeightDist - self.minCamHeightDist) / 2.0 + self.minCamHeightDist
            # the initial cam height
            self.camHeight = self.camHeightAvg
            # a time to keep the cam zoom at a specific speed independent of
            # current framerate
            self.camElapsed = 0.0
            # an invisible object which will fly above the player and will be used to
            # track the camera on it
            self.camFloater = NodePath(PandaNode("playerCamFloater"))
            self.camFloater.reparentTo(self.render)

            self.taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

    def setKey(self, key, value):
        self.keyMap[key] = value

    def move(self, task):
        startpos = self.spaceship.getPos()
        if self.keyMap["left"] != 0:
            self.spaceship.setH(self.spaceship.getH() + 300 * globalClock.getDt())
        if self.keyMap["right"] != 0:
            self.spaceship.setH(self.spaceship.getH() - 300 * globalClock.getDt())
        if self.keyMap["forward"] != 0:
            self.spaceship.setY(self.spaceship, -25 * globalClock.getDt())
        if self.keyMap["backward"] !=0:
            self.spaceship.setX(self.spaceship, 25 * globalClock.getDt())
        if self.keyMap["up"] != 0:
            self.spaceship.setZ(self.spaceship.getZ() + 25 * globalClock.getDt())
        if self.keyMap["down"] != 0:
            self.spaceship.setZ(self.spaceship.getZ() - 25 * globalClock.getDt())

        return task.cont

    def update(self, task):
        dt = globalClock.getDt()
        self.world.doPhysics(dt)

        # result = self.world.rayTestAll(
        #    self.camera.getPos(),
        #    )

        return task.cont

    def zoom(self, zoomIn):
        if zoomIn:
            if self.maxCamDistance > self.minCamDistance:
                self.maxCamDistance = self.maxCamDistance - 0.5
            self.acceptOnce("+", self.zoom, [True])
        else:
            if self.maxCamDistance < self.maxCamDistance:
                self.maxCamDistance = self.maxCamDistance + 0.5
            self.acceptOnce("-", self.zoom, [False])

    def updateCam(self, task):
        """This function will check the min and max distance of the camera to
        the defined model and will correct the position if the cam is to close
        or to far away"""

        # Camera Movement Updates
        camvec = self.spaceship.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()

        # If far from player start following
        if camdist > self.maxCamDistance:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - self.maxCamDistance))
            camdist = self.maxCamDistance

        # If player to close move cam backwards
        if camdist < self.minCamDistance:
            self.camera.setPos(self.camera.getPos() - camvec * (self.minCamDistance - camdist))
            camdist = self.minCamDistance

        # get the cameras current offset to the player model on the z-axis
        offsetZ = self.camera.getZ() - self.spaceship.getZ()
        # check if the camera is within the min and max z-axis offset
        if offsetZ < self.minCamHeightDist:
            self.camera.setZ(self.spaceship.getZ() + self.minCamHeightDist)
            offsetZ = self.minCamHeightDist
        elif offsetZ > self.maxCamHeightDist:
            self.camera.setZ(self.spaceship.getZ() + self.maxCamHeightDist)
            offsetZ = self.maxCamHeightDist

        if offsetZ != self.camHeightAvg:
            # if we are not moving up or down, set the cam to an average position
            if offsetZ != self.camHeightAvg:
                if offsetZ > self.camHeightAvg:
                    # the cam is higher then the average cam height above the player
                    # so move it slowly down
                    self.camera.setZ(self.camera.getZ() - 5 * globalClock.getDt())
                    newOffsetZ = self.camera.getZ() - self.spaceship.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ < self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        self.camera.setZ(self.spaceship.getZ() + self.camHeightAvg)
                else:
                    # the cam is lower then the average cam height above the player
                    # so move it slowly up
                    self.camera.setZ(self.camera.getZ() + 5 * globalClock.getDt())
                    newOffsetZ = self.camera.getZ() - self.spaceship.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ > self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        self.camera.setZ(self.spaceship.getZ() + self.camHeightAvg)

        if self.keyMap["center"]:
            self.camera.setPos(self.spaceship, 0, camdist, offsetZ)

        self.camFloater.setPos(self.spaceship.getPos())
        self.camFloater.setX(self.spaceship.getX() + self.lookatOffset.getX())
        self.camFloater.setY(self.spaceship.getY() + self.lookatOffset.getY())
        self.camFloater.setZ(self.spaceship.getZ() + self.lookatOffset.getZ())
        self.camera.lookAt(self.spaceship)

        # continue the task until it got manually stopped
        return task.cont




game = Game()
game.run()
