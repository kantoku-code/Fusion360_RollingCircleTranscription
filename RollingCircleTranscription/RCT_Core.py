#FusionAPI_python Addin
#Author-kantoku
#Description-RollingCircleTranscription

import adsk.core, adsk.fusion, traceback
import math, time
from fractions import Fraction

# 比率に対しての制限
RATIO_APPROXIMATION_LEVEL = 20
DEBUG = False

class RCT_Factry():

    _app = adsk.core.Application.cast(None)
    _ui = adsk.core.UserInterface.cast(None)
    _cg = None

    _baseProfile = adsk.fusion.Profile.cast(None)
    @property
    def baseProfile(self):
        return self._baseProfile

    @baseProfile.setter
    def baseProfile(self, value):
        self._baseProfile = value


    _baseCircle = adsk.fusion.SketchCircle.cast(None)
    @property
    def baseCircle(self):
        return self._baseCircle

    @baseCircle.setter
    def baseCircle(self, value):
        self._baseCircle = value


    _targetCircle = adsk.fusion.SketchCircle.cast(None)
    @property
    def targetCircle(self):
        return self._targetCircle

    @targetCircle.setter
    def targetCircle(self, value):
        self._targetCircle = value


    def __init__(self):
        self._app = adsk.core.Application.get()
        self._ui = self._app.userInterface
        self._cg = DrawCGFactry(self._app)

        # extended method
        adsk.fusion.SketchCircle.plane = getSktPlane
        adsk.fusion.Profile.plane = getSktPlane


    def __del__(self):
        self._cg.removeCG()
        del self._cg


    def _getFraction(self):
        if not self._targetCircle or not self._baseCircle:
            return None
        
        baseR = self._baseCircle.radius
        targetR =self._targetCircle.radius
        try:
            fra = Fraction(baseR / targetR)
        except:
            return None

        ratio = baseR / targetR
        fra = Fraction(ratio).limit_denominator(RATIO_APPROXIMATION_LEVEL)
        return [fra.numerator, fra.denominator]


    def canExec(self):
        try:
            ents = {
                'Base Profile':self._baseProfile,
                'Base Circle':self._baseCircle,
                'Target Circle':self._targetCircle
                }

            # 選択無し
            for ent in ents.values():
                if not ent:
                    return False, ''

            msg = []
            for key in ents.keys():
                ent = ents[key]

                # is2D
                if hasattr(ent, 'is2D'):
                    if not ent.is2D:
                        msg.append("It's not an element on the sketch plane:{}".format(key))

                # baseProfile baseCircle targetCircle 同一平面上チェック
                for tgtkey in ents.keys():
                    tgt = ents[tgtkey]
                    if ent == tgt:
                        continue

                    if not ent.plane().isCoPlanarTo(tgt.plane()):
                        msg.append("Not on the same plane:{} , {}".format(key, tgtkey))


            # baseCircle-targetCircle 比率チェック
            res = self._getFraction()
            if not res:
                msg.append("The ratio of circles to each other should be a rational number.:Base Circle , Target Circle")


            if len(msg) < 1:
                return True, 'Base Rotation Count:{}\nTarget Rotation Count:{}'.format(res[1], res[0])
            else:
                return False, '\n'.join(msg)

        except:
            self._ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def execute(
        self,
        targetAngle :int,
        previewStep = 2
        ) -> adsk.core.Surface:

        def dumpMsg(msg :str):
            self._ui.palettes.itemById('TextCommands').writeText(str(msg))

        try:
            # check
            res, _ = self.canExec()
            if not res:
                return

            tmpMgr = adsk.fusion.TemporaryBRepManager.get()

            # base surface
            crvs = []
            for loop in self._baseProfile.profileLoops:
                crvs.extend([c.geometry for c in loop.profileCurves])

            wireBodies = tmpMgr.createWireFromCurves(crvs)
            baseSurf = tmpMgr.createFaceFromPlanarWires([wireBodies[0]])

            # target surface
            wireBodies = tmpMgr.createWireFromCurves([self._targetCircle.geometry])
            targetSurf = tmpMgr.createFaceFromPlanarWires([wireBodies[0]])

            # target-base ratio
            ratio = self._targetCircle.radius / self._baseCircle.radius
            targetCount, _ = self._getFraction()
            if DEBUG:
                dumpMsg('ratio  {}'.format(ratio))
                dumpMsg('getFraction  {}:{}'.format(_, targetCount))

            count :int = int(abs(360 * targetCount / targetAngle))
            rad = math.radians(targetAngle)

            # mat-base
            mat3D = adsk.core.Matrix3D
            baseMat :adsk.core.Matrix3D = mat3D.create()
            baseMat.setToRotation(
                rad * ratio, 
                self._baseCircle.geometry.normal, 
                self._baseCircle.geometry.center)

            # mat-target
            targetMat :adsk.core.Matrix3D = mat3D.create()
            targetMat.setToRotation(
                rad * -1,
                self._targetCircle.geometry.normal,
                self._targetCircle.geometry.center)

            # create target
            t = time.time()

            # return
            optDiff = adsk.fusion.BooleanTypes.DifferenceBooleanType
            for idx in range(count):
                tmpMgr.transform(baseSurf, baseMat)
                tmpMgr.transform(targetSurf, targetMat)
                tmpMgr.booleanOperation(targetSurf, baseSurf, optDiff)

                if idx % previewStep == 0:
                    self._cg.update(baseSurf, targetSurf)
                    adsk.doEvents()
                    self._app.activeViewport.refresh()

            dumpMsg('{:.3f}sec'.format(time.time() - t))

            self._cg.removeCG()
            return targetSurf

        except:
            self._ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


    def initSurface(
        self,
        surf :adsk.core.Surface,
        comp :adsk.fusion.Component = None
        ) -> adsk.fusion.BRepBody:

        des :adsk.fusion.Design = self._app.activeDocument.design

        if not comp:
            comp = des.rootComponent

        bodies = comp.bRepBodies

        brep = adsk.fusion.BRepBody.cast(None)

        if des.designType == adsk.fusion.DesignTypes.DirectDesignType:
            brep = bodies.add(surf)
        else:
            baseFeatures = comp.features.baseFeatures
            baseFeature = baseFeatures.add()
            try:
                baseFeature.startEdit()
                brep = bodies.add(surf, baseFeature)
            except:
                pass
            finally:
                baseFeature.finishEdit()

        return brep

class DrawCGFactry():

    _app = adsk.core.Application.cast(None)
    _cgGroup = adsk.fusion.CustomGraphicsGroup.cast(None)

    red = adsk.core.Color.create(255,0,0,255)
    _solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(red)
    blue = adsk.core.Color.create(0,0,255,255)
    _solidBlue = adsk.fusion.CustomGraphicsSolidColorEffect.create(blue)

    def __init__(self, app):
        self._app = app
        self.refreshCG()

    def __del__(self):
        self.removeCG()

    def removeCG(self):
        des :adsk.fusion.Design = self._app.activeProduct
        cgs = [cmp.customGraphicsGroups for cmp in des.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]
        
        if len(cgs) < 1: return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                gp.deleteMe()

    def refreshCG(self):
        self.removeCG()
        des :adsk.fusion.Design = self._app.activeProduct
        root :adsk.fusion.Component = des.rootComponent
        self._cgGroup = root.customGraphicsGroups.add()

    def update(self, baseSurf, targetSurf):
        self.refreshCG()

        cgBdy = self._cgGroup.addBRepBody(baseSurf)
        cgBdy.color = self._solidBlue
        cgBdy.weight = 2

        cgBdy = self._cgGroup.addBRepBody(targetSurf)
        cgBdy.color = self._solidRed
        cgBdy.weight = 2


# extended method
def getSktPlane(self) -> adsk.core.Plane:
    skt :adsk.fusion.Sketch = self.parentSketch
    vec = skt.xDirection.crossProduct(skt.yDirection)
    return adsk.core.Plane.create(skt.origin, vec)