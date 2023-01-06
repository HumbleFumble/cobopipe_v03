import pymel.core as pm

def createRibbon(name=None, driverNum=5, drivenNum=9):
    if name == None:
        name = 'ribbon'
    ribbon, history = pm.nurbsPlane(name=name + '_NRB', ax=(0, 1, 0), u=driverNum-1)
    pm.delete(history)

    # temporary
    # ribbon.scaleX.set(5)
    #

    follicleGroup = pm.group(name=name + '_follicles', empty=True, world=True)
    drivenJointGroup = pm.group(name=name + '_drivenJoints', empty=True, world=True)
    driverJointGroup = pm.group(name=name + '_driverJoints', empty=True, world=True)
    
    for i in range(drivenNum):
        position = (1.0/float(drivenNum-1)) * float(i)
        follicle = createFollicle(ribbon.getShape(), position, v=0.5)
        pm.parent(follicle, follicleGroup)

        follicleName = ''.join([name, str(i+1).zfill(2), '_Fol'])
        pm.rename(follicle, follicleName)
        
        jointName = ''.join([name, 'Driven', str(i+1).zfill(2), '_Jnt'])
        joint = pm.joint(follicle, name=jointName, radius=0.1)
        pm.parent(joint, drivenJointGroup)
        pm.parentConstraint(follicle, joint)
        pm.scaleConstraint(follicle, joint)


    driverJoints = []
    for i in range(driverNum):
        pm.select(deselect=True)
        jointName = ''.join([name, 'Driver', str(i+1).zfill(2), '_Jnt'])
        joint = pm.joint(name=jointName, radius=0.5)
        position = ((1.0/float(driverNum-1)) * float(i)) - 0.5
        joint.tx.set(position)
        pm.parent(joint, driverJointGroup)
        driverJoints.append(joint)

    skinCluster = pm.skinCluster(driverJoints, ribbon, dr=0.5)
    for i in range(len(ribbon.cv)/4):
        for cv in ribbon.cv[i]:
            if i == 0:
                pm.skinPercent(skinCluster, cv, transformValue=(driverJoints[i], 1.0))
            elif i == 1:
                pm.skinPercent(skinCluster, cv, transformValue=(driverJoints[i-1], 1.0))
            elif 1 < i < driverNum:
                pm.skinPercent(skinCluster, cv, transformValue=(driverJoints[i-1], 1.0))
            elif i == driverNum:
                pm.skinPercent(skinCluster, cv, transformValue=(driverJoints[i-1], 1.0))
            elif i == driverNum + 1:
                pm.skinPercent(skinCluster, cv, transformValue=(driverJoints[i-2], 1.0))
            else:
                print('ERROR: Too many segments. i = ' + str(i))
                

def createFollicle(shape, u=0.0, v=0.0):
    name = '_'.join([shape.name(),'follicle','#'.zfill(2)])
    follicle = pm.createNode('follicle', name=name)
    if shape.type() == 'nurbsSurface':
        shape.local.connect(follicle.inputSurface)
    elif shape.type() == 'mesh':
        shape.outMesh.connect(follicle.inMesh) # Polygons must have UVs

    shape.worldMatrix[0].connect(follicle.inputWorldMatrix)
    follicle.outRotate.connect(follicle.getParent().rotate)
    follicle.outTranslate.connect(follicle.getParent().translate)
    follicle.parameterU.set(u)
    follicle.parameterV.set(v)
    follicle.getParent().t.lock()
    follicle.getParent().r.lock()

    return follicle.getParent()