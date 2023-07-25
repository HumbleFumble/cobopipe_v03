import os
from pxr import Usd

folder = os.path.dirname(__file__)
stage = Usd.Stage.CreateNew(folder + '/files/HelloWorldRedux.usda')
xform = stage.DefinePrim('/hello', 'Xform')
sphere = stage.DefinePrim('/hello/world', 'Sphere')
stage.GetRootLayer().Save()