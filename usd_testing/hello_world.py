import os
from pxr import Usd, UsdGeom

folder = os.path.dirname(__file__)
stage = Usd.Stage.CreateNew(folder + "/files/HelloWorld.usda")
xformPrim = UsdGeom.Xform.Define(stage, "/hello")
spherePrim = UsdGeom.Sphere.Define(stage, "/hello/world")
stage.GetRootLayer().Save()
