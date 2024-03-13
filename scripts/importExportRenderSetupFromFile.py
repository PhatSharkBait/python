import maya.app.renderSetup.model.renderSetup as renderSetup

import json


def importRenderSetup(filename):
    with open(filename, "r") as file:
        renderSetup.instance().decode(json.load(file), renderSetup.DECODE_AND_OVERWRITE, None)


def exportRenderSetup(filename, note=None):
    with open(filename, "w+") as file:
        json.dump(renderSetup.instance().encode(note), fp=file, indent=2, sort_keys=True)


def main():
    exportRenderSetup("Z:/exportedRenderSetup.json", note=None)


if __name__ == '__main__':
    main()