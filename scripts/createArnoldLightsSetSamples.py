import maya.cmds as cmds
from functools import partial

numberOfSamples = 3


def create_light_and_close(button_collection, close_after, window, *args):
    light_selection = cmds.radioCollection(button_collection, q=True, sl=True)
    if light_selection == "Area_Light":
        create_area_light()
    elif light_selection == "Skydome_Light":
        create_skydome_light()
    elif light_selection == "Mesh_Light":
        create_mesh_light()
    elif light_selection == "Photometric_Light":
        create_photometric_light()
    #elif light_selection == "Light_Portal":
        #create_light_portal()
    #elif light_selection == "Physical_Sky":
        #create_physical_sky()
    else:
        cmds.warning("how did you even do that?")
        print(light_selection)

    if close_after is True:
        cmds.deleteUI(window)


def create_window():
    window = 'CreateArnoldLight'
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)

    window = cmds.window(window, title="Create Arnold Light", widthHeight=[300, 400], resizeToFitChildren=1)

    main_column = cmds.columnLayout(parent=window, adjustableColumn=1)
    radio_button_layout = cmds.rowColumnLayout(parent=main_column, numberOfColumns=2, cs=(2, 40))

    button_collection = cmds.radioCollection(parent=radio_button_layout)
    button1 = cmds.radioButton("Area Light", collection=button_collection)
    button2 = cmds.radioButton("Skydome Light", collection=button_collection)
    button3 = cmds.radioButton("Mesh Light", collection=button_collection)
    button4 = cmds.radioButton("Photometric Light", collection=button_collection)
    #button5 = cmds.radioButton("Light Portal", collection=button_collection)
    #button6 = cmds.radioButton("Physical Sky", collection=button_collection)

    function_button_Layout = cmds.rowColumnLayout(parent=main_column, numberOfColumns=3)

    cmds.button("Create Light", command=partial(create_light_and_close, button_collection, True, window))
    cmds.button("Add Light", command=partial(create_light_and_close, button_collection, False, window))
    cmds.button("Close", command=partial(close_window, window))

    cmds.showWindow(window)

    cmds.radioCollection(button_collection, edit=True, sl=button1)

def create_area_light():
    cmds.cmdArnoldAreaLights()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def create_skydome_light():
    cmds.cmdSkydomeLight()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def create_mesh_light():
    cmds.cmdArnoldMeshLight()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def create_photometric_light():
    cmds.cmdPhotometricLights()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def create_light_portal():
    cmds.cmdLightPortal()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def create_physical_sky():
    cmds.cmdPhysicalSky()
    light_shape = cmds.listRelatives(children=True)[0]
    cmds.setAttr('%s.aiSamples' % light_shape, numberOfSamples, lock=True)


def close_window(window, *args):
    cmds.deleteUI(window)


if __name__ == '__main__':
    cmds.setToolTo('selectSuperContext')
    create_window()
