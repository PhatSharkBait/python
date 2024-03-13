import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.cmds as cmds
import json

def setupRenderLayers(renderSettingsFile):
    rs = renderSetup.instance()

    with open(renderSettingsFile, "r") as file:
        rs.decode(json.load(file), renderSetup.DECODE_AND_OVERWRITE, None)


def createCustomShaders():
    shadowShaderName = "aiShadowMatteAOV"
    ambientOcclusionShaderName = "aiAmbientOcclusionAOV"

    shadowMatteMaterial = cmds.shadingNode('aiShadowMatte', name=shadowShaderName, asShader=True)

    ambientOcclusionMaterial = (
        cmds.shadingNode('aiAmbientOcclusion', name=ambientOcclusionShaderName, asShader=True))

    if not cmds.objExists("utilityFlatSG"):
        flatMaterial = cmds.shadingNode('aiFlat', name = "utilityFlat", asShader=True)
        flatShadingGroup = cmds.shadingNode('shadingEngine', name = "utilityFlatSG", asUtility=True)
        cmds.connectAttr(flatMaterial + ".outColor", flatShadingGroup + ".surfaceShader")

    return ["aiAOV_ShadowMatte", shadowMatteMaterial], ["aiAOV_AmbientOcclusion", ambientOcclusionMaterial]


def connectCustomShaders(customShaders):
    for customShader in customShaders:
        cmds.connectAttr(customShader[1] + ".outColor", customShader[0] + ".defaultValue", force=True)


def importRenderSettings():

    renderSettingsFilePath = cmds.fileDialog2(selectFileFilter=".json", dialogStyle=2, fileMode=1)[0]

    if renderSettingsFilePath:
        customShaders = createCustomShaders()
        setupRenderLayers(renderSettingsFilePath)
        connectCustomShaders(customShaders)


def main():
    importRenderSettings()


if __name__ == '__main__':
    main()

