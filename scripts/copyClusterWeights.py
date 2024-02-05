#Select only 2 cluster handles
#1st selection will be the SOURCE weights
#2nd selection will be the RECEIVING weights

import maya.cmds as cmds

sels = cmds.ls(sl=True)

clusterCopyFrom = cmds.listConnections(sels[0], type="cluster")[0]
clusterCopyTo = cmds.listConnections(sels[1], type="cluster")[0]

clusterComponents = cmds.cluster(clusterCopyFrom, query=True, cmp=True)

components = []
for clusterComponent in clusterComponents:
    if ":" in clusterComponent:
        object_name, component_string = clusterComponent.split(".")
        start, end = map(int, component_string[4:-1].split(":"))
        for i in range(start, end + 1):
            components.append(f"{object_name}.vtx[{i}]")
    else:
        components.append(clusterComponent)

for vertex in components:
    valueToCopy = cmds.percent(clusterCopyFrom, vertex, query=True, v=True)[0]
    cmds.percent(clusterCopyTo, vertex, v=valueToCopy)

print("copied %s to %s" % (clusterCopyFrom, clusterCopyTo))