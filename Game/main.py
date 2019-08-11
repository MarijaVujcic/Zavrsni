import sys

from direct.showbase.ShowBase import ShowBase, SamplerState, Shader
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Vec3
from panda3d.core import NodePath, PandaNode

class Runner(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept("escape", sys.exit)
        skybox = self.loader.loadModel("Assets/skybox.bam")
        skybox.reparent_to(self.render)
        skybox.set_scale(200000)
        skybox_texture = self.loader.loadTexture("Assets/stars.jpg")
        skybox_texture.set_minfilter(SamplerState.FT_linear)
        skybox_texture.set_magfilter(SamplerState.FT_linear)
        skybox_texture.set_wrap_u(SamplerState.WM_repeat)
        skybox_texture.set_wrap_v(SamplerState.WM_mirror)
        skybox_texture.set_anisotropic_degree(16)
        skybox.set_texture(skybox_texture)


        # simple Player setup
        self.keyMap = {"left":0, "right":0, "forward":0, "up":0, "down":0, "center":0}
        self.player = self.loader.loadModel("Assets/Characters/spaceship")
        self.player.setPos(0, 10, 1)
        self.player.reparentTo(self.render)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("w", self.setKey, ["up",1])
        self.accept("w-up", self.setKey, ["up",0])
        self.accept("s", self.setKey, ["down",1])
        self.accept("s-up", self.setKey, ["down",0])
        self.accept("q", self.setKey, ["center",1])
        self.accept("q-up", self.setKey, ["center",0])
        self.taskMgr.add(self.move, "moveTask")

        # Camera
        #
        self.acceptOnce("+", self.zoom, [True])
        self.acceptOnce("-", self.zoom, [False])
        # disable pandas default mouse-camera controls so we can handle the cam
        # movements by ourself
        self.disableMouse()
        # the next two vars will set the min and max distance the cam can have
        # to the node it is attached to
        self.maxCamDistance = 200.0
        self.minCamDistance = 100.0
        # the initial cam distance
        self.camDistance = (self.maxCamDistance - self.minCamDistance) / 2.0 + self.minCamDistance
        # the next two vars set the min and max distance on the Z-Axis to the
        # node the cam is attached to
        self.maxCamHeightDist = 4.0
        self.minCamHeightDist = 2.0
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
        # the following will set an offset to the node this floater is attached to
        self.camFloater.setPos(0, 0, 1)
        self.camFloater.reparentTo(self.player)


        self.taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

    #
    # SIMPLE PLAYER FUNCTIONALITY
    #
    def setKey(self, key, value):
        self.keyMap[key] = value

    def move(self, task):
        if self.keyMap["left"] != 0:
            self.player.setH(self.player.getH() + 300 * globalClock.getDt())
        if self.keyMap["right"] != 0:
            self.player.setH(self.player.getH() - 300 * globalClock.getDt())
        if self.keyMap["forward"] != 0:
            self.player.setY(self.player, -25 * globalClock.getDt())
        if self.keyMap["up"] != 0:
            self.player.setZ(self.player.getZ() + 25 * globalClock.getDt())
        if self.keyMap["down"] != 0:
            self.player.setZ(self.player.getZ() - 25 * globalClock.getDt())

        return task.cont

    #
    # CAMERA FUNCTIONALITY
    #
    def zoom(self, zoomIn):
        if zoomIn:
            if self.maxCamDistance > self.minCamDistance:
                self.maxCamDistance = self.maxCamDistance - 0.5
            self.acceptOnce("+", self.zoom, [True])
        else:
            if self.maxCamDistance < 15: # 15 is the default maximum
                self.maxCamDistance = self.maxCamDistance + 0.5
            self.acceptOnce("-", self.zoom, [False])


    def updateCam(self, task):
        """This function will check the min and max distance of the camera to
        the defined model and will correct the position if the cam is to close
        or to far away"""

        # Camera Movement Updates
        camvec = self.player.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()

        # If far from player start following
        if camdist > self.maxCamDistance:
            self.camera.setPos(self.camera.getPos() + camvec*(camdist-self.maxCamDistance))
            camdist = self.maxCamDistance

        # If player to close move cam backwards
        if camdist < self.minCamDistance:
            self.camera.setPos(self.camera.getPos() - camvec*(self.minCamDistance-camdist))
            camdist = self.minCamDistance

        # get the cameras current offset to the player model on the z-axis
        offsetZ = self.camera.getZ() - self.player.getZ()
        # check if the camera is within the min and max z-axis offset
        if offsetZ < self.minCamHeightDist:
            # the cam is to low, so move it up
            self.camera.setZ(self.player.getZ() + self.minCamHeightDist)
            offsetZ = self.minCamHeightDist
        elif offsetZ > self.maxCamHeightDist:
            # the cam is to high, so move it down
            self.camera.setZ(self.player.getZ() + self.maxCamHeightDist)
            offsetZ = self.maxCamHeightDist

        # lazy camera positioning
        if offsetZ != self.camHeightAvg:
            # if we are not moving up or down, set the cam to an average position
            if offsetZ != self.camHeightAvg:
                if offsetZ > self.camHeightAvg:
                    # the cam is higher then the average cam height above the player
                    # so move it slowly down
                    self.camera.setZ(self.camera.getZ() - 5 * globalClock.getDt())
                    newOffsetZ = self.camera.getZ() - self.player.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ < self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        self.camera.setZ(self.player.getZ() + self.camHeightAvg)
                else:
                    # the cam is lower then the average cam height above the player
                    # so move it slowly up
                    self.camera.setZ(self.camera.getZ() + 5 * globalClock.getDt())
                    newOffsetZ = self.camera.getZ() - self.player.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ > self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        self.camera.setZ(self.player.getZ() + self.camHeightAvg)

        # center the camera as long as the center key is pressed
        if self.keyMap["center"]:
            self.camera.setPos(self.player, 0, camdist, offsetZ)

        # let the camera look at the floater
        self.camera.lookAt(self.camFloater)

        # continue the task until it got manually stopped
        return task.cont

runner = Runner()
runner.run()
