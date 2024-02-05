import maya.cmds as cmds
import re
import sys
import os
from random import *
import maya.mel as mel
import pymel.core as pm

W = 160
W2 = 130

## Set Path to match the location. ##
'''


import importlib
import maya.cmds as cmds
sys.path.append("E:\Projects\Spring2023\Maya\Scripts\GNC_RS_Toon_Shader_Tool.py")
import GNC_RS_Toon_Shader_Tool
importlib.reload(GNC_RS_Toon_Shader_Tool)
GNC_RS_Toon_Shader_Tool.Toon_Setup()



'''

toon_window = 'toon_window'
sub_number_amount = 'subNum'
disNum22 = 'disNum'
minEdge22 = 'minEdge'
ObjectIDNum = 'ObjectIDNumber'


if cmds.window(toon_window, exists=True ):
    cmds.deleteUI(toon_window)
W = 250
W2 = 400
spacing = 2
color_name_input = None
selection_tool_search = None
Color_Name = ''
Color_R = None
Color_G = None
Color_B = None
light_samples_number = 'float_list'
attr_template = "{}.{}"

class gnc_toon_shader():
    def __init__(self, *args):

        self.make_toonshader()
    ## These are pre created format for selection and attriubutes ##
    def selection_format(self, selection, name):

        return "{}_{}".format(selection, name)
    def attr_format(self, selection, name):

        return "{}.{}".format(selection, name)
    def first_selection(self, *args):

        return cmds.ls(sl=True)[0]
    def overall_sel(self, *args):

        return cmds.listRelatives(children=True, pa= True, allDescendents = True, type='mesh')
    def make_shading_node(self, name, node_type, shading_type, parent=True):
        if cmds.objExists(name):
            print('{} already exists'.format(name))
            return name
        args = (node_type, )
        kwargs = {shading_type: True, 'name':name}
        if parent is not None:
            kwargs['parent'] = parent
        return cmds.shadingNode(*args, **kwargs)
    def make_toonshader(self, *args):
        selection = self.first_selection()
        sel = self.overall_sel()

        def make_node( name, node_type, shading_type):
            node_name = self.selection_format(selection, name)
            if cmds.objExists(node_name):
                cmds.delete(node_name)
            return self.make_shading_node(node_name, node_type, shading_type)

        name_mat = selection + '_ms_toon'
        if cmds.objExists(name_mat):
            pass
            print(name_mat + ' already exists')
        else:
            self.toon_light = self.get_or_make_toon_light()
            # toon utility pieces
            self.decompose_matrix = make_node('decompose_matrix', 'decomposeMatrix', 'asUtility')
            self.mult_div_a = make_node('mult_div_a', 'multiplyDivide', 'asUtility')
            self.mult_div_b = make_node('mult_div_b', 'multiplyDivide', 'asUtility')
            self.mult_div_c = make_node('mult_div_c', 'multiplyDivide', 'asUtility')
            self.plus_minus = make_node('plus_minus', 'plusMinusAverage', 'asUtility')
            self.rs_state = make_node('state', 'RedshiftState', 'asUtility')
            self.vector_product = make_node('vector_product', 'vectorProduct', 'asUtility')
            self.remap_value = make_node('remap_value', 'remapValue', 'asUtility')
            self.zone_control = make_node('ZONE_CONTROL', 'ramp', 'asTexture')
            self.rs_data = make_node('rs_data', 'RedshiftUserDataColor', 'asUtility')
            self.rs_matte_shad = make_node('ms_toon', 'RedshiftMatteShadowCatcher', 'asShader')
            self.aov_toon = mel.eval('shadingNode -asTexture RedshiftStoreColorToAOV;')
            self.rs_aov_name = selection + '_AOV_data'
            self.rs_color_to_aov_b = cmds.rename(self.aov_toon, self.rs_aov_name)
            cmds.select(self.rs_color_to_aov_b)  
            self.shader_grp_name = selection + '_SG'
            self.shader_grp = cmds.sets(name=self.shader_grp_name, empty=True, renderable=True, noSurfaceShader=True)
            cmds.sets(sel, e=True, forceElement = self.shader_grp)
            # connect Material to Shader Group
            attr_template = "{}.{}"
            connection_a = attr_template.format(self.rs_aov_name, 'outColor')
            connection_b = attr_template.format(self.shader_grp_name, 'surfaceShader')
            cmds.connectAttr(connection_a, connection_b, force=True )
            self.node_Connections_and_overrides()
            self.custom_aov()
    def node_Connections_and_overrides(self, *args):

        attr_template = "{}.{}"
        shape_template = "{}{}"
        self.selection = self.first_selection()
        self.toon_light = self.get_or_make_toon_light()

        # This part of the script will connect and set the settings correctly
        # Connecting Decompose Matrix to light
        connection_a = shape_template.format(self.toon_light, 'Shape.worldMatrix[0]')
        connection_b = attr_template.format(self.decompose_matrix, 'inputMatrix')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # connect Dec. matrix to Mult Div
        connection_a = attr_template.format(self.decompose_matrix, 'outputTranslate')
        connection_b = attr_template.format(self.mult_div_a, 'input1')
        cmds.connectAttr(connection_a, connection_b, force=True )

        # Connecting mult div a  to plus min A input 0
        connection_a = attr_template.format(self.mult_div_a, 'output')
        connection_b = attr_template.format(self.plus_minus, 'input3D[0]')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # Settings sets operation to Subtract
        attr_setting = attr_template.format(self.plus_minus, 'operation')
        cmds.setAttr(attr_setting, 2)

         # Connecting state to plus min A input 1
        connection_a = attr_template.format(self.rs_state, 'outTangent')
        connection_b = attr_template.format(self.plus_minus, 'input3D[1]')
        cmds.connectAttr(connection_a, connection_b, force=True)    

        # Connecting  plus min A  to vector product input A
        connection_a = attr_template.format(self.plus_minus, 'output3D')
        connection_b = attr_template.format(self.vector_product, 'input2')
        cmds.connectAttr(connection_a, connection_b, force=True)
        
        # Connecting state to vector procuct input 2
        connection_a = attr_template.format(self.rs_state, 'outBumpNormal')
        connection_b = attr_template.format(self.vector_product, 'input1')
        cmds.connectAttr(connection_a, connection_b, force=True)
        # Settings
        attr_setting_a = attr_template.format(self.rs_state, 'trans_space')
        cmds.setAttr(attr_setting_a, 1)

        # Connecting vector procuct x to Toon Control
        connection_a = attr_template.format(self.vector_product, 'outputX')
        connection_b = attr_template.format(self.remap_value, 'inputValue')
        cmds.connectAttr(connection_a, connection_b, force=True)
        

        # Connecting vector procuct x to Toon Control
        connection_a = attr_template.format(self.remap_value, 'outValue')
        connection_b = attr_template.format(self.zone_control, 'vCoord')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # Connecting Toon control to MultiplyDivide_B
        connection_a = attr_template.format(self.zone_control, 'outColor')
        connection_b = attr_template.format(self.mult_div_b, 'input1')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # Connecting Toon control to MultiplyDivide_B
        connection_a = attr_template.format(self.toon_light, 'color')
        connection_b = attr_template.format(self.mult_div_b, 'input2')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # Connecting MultiplyDivide_B to RS_Matte_Shadow_Catcher
        connection_a = attr_template.format(self.mult_div_b, 'output')
        connection_b = attr_template.format(self.rs_matte_shad, 'background')
        cmds.connectAttr(connection_a, connection_b, force=True)
        
        # Connecting RS_Matte_Shadow_Catcher to MultiplyDivide_B
        connection_a = attr_template.format(self.rs_matte_shad, 'outColor')
        connection_b = attr_template.format(self.rs_aov_name, 'beauty_input')
        cmds.connectAttr(connection_a, connection_b, force=True)
        
        
        # Connecting zone_control to Toon
        connection_a = attr_template.format(self.mult_div_b, 'output')
        connection_b = attr_template.format(self.rs_aov_name, 'aov_input_list[1].input')
        cmds.connectAttr(connection_a, connection_b, force=True)
        
        # Connecting RS_data to zone control
        connection_a = attr_template.format(self.rs_data, 'out')
        connection_b = attr_template.format(self.zone_control, 'colorEntryList[0].color')
        cmds.connectAttr(connection_a, connection_b, force=True)


        # Connecting Toon control to MultiplyDivide_B
        connection_a = attr_template.format(self.toon_light, 'color')
        connection_b = attr_template.format(self.mult_div_c, 'input2')
        cmds.connectAttr(connection_a, connection_b, force=True)


        # Connecting RS_data to Matte_Shadows shadow
        connection_a = attr_template.format(self.rs_data, 'out')
        connection_b = attr_template.format(self.mult_div_c, 'input1')
        cmds.connectAttr(connection_a, connection_b, force=True)

        # Connecting RS_data to Matte_Shadows shadow
        connection_a = attr_template.format(self.mult_div_c, 'output')
        connection_b = attr_template.format(self.rs_matte_shad, 'shadows')
        cmds.connectAttr(connection_a, connection_b, force=True)

        ## Settings for Nodes ##
        
        # Settings for Ramp Zone Positions and colors

        attr_setting_b = attr_template.format(self.zone_control, 'colorEntryList[1].position')
        cmds.setAttr(attr_setting_b, 0.68)
        attr_setting_c = attr_template.format(self.zone_control, 'colorEntryList[0].position')
        cmds.setAttr(attr_setting_c, 0)
        attr_setting_d = attr_template.format(self.zone_control, 'interpolation')
        cmds.setAttr(attr_setting_d, .0)

        attr_setting_e = attr_template.format(self.rs_data, 'default')
        cmds.setAttr(attr_setting_e, 0.276596, 0.276596, 0.276596)
        attr_setting_f = attr_template.format(self.zone_control, 'colorEntryList[1].color')
        cmds.setAttr(attr_setting_f, 0.425532, 0.425532, 0.425532)

        # Multiply divide settings 
        attr_setting_a = attr_template.format(self.mult_div_a, 'input2Z')
        cmds.setAttr(attr_setting_a, 1)
        
        # change name of AOVs for the toon shaders
        attr_setting_a = attr_template.format(self.rs_aov_name, 'aov_input_list[1].name')
        cmds.setAttr(attr_setting_a, 'Toon_Colors', type="string")

        # Set the settings for  Plus minus
        attr_setting_y = attr_template.format(self.plus_minus, 'operation')
        cmds.setAttr(attr_setting_y, 1)
    def get_or_make_toon_light(self, *args):
        attr_template = "{}.{}"
        shape_template = "{}{}" 
        light_name = 'LGT_Toon_Light'
        light_name_shape = shape_template.format(light_name, 'Shape')
        if cmds.objExists(light_name):
            return light_name
        else:
            toon_light_transform = cmds.group(empty=True, name=light_name)
            cmds.shadingNode('RedshiftPhysicalLight', name='LGT_Toon_LightShape', asLight=True, parent=toon_light_transform)
            # Toon Light Settings
            attr_setting_a = attr_template.format(light_name, 'lightType')
            cmds.setAttr(attr_setting_a, 1)
            attr_setting_b = attr_template.format(light_name, 'intensity')
            cmds.setAttr(attr_setting_b, 1)
            attr_setting_c = attr_template.format(light_name, 'exposure')
            cmds.setAttr(attr_setting_c, 2)
           # Toon Light Settings
            attr_setting_a = attr_template.format(light_name, 'translateX')
            cmds.setAttr(attr_setting_a, 15)
            attr_setting_b = attr_template.format(light_name, 'translateY')
            cmds.setAttr(attr_setting_b, 5)
    def custom_aov(self, *args):
        attr_template = "{}.{}"
        shape_template = "{}{}"
        name_custom = 'Toon_Colors'
        if cmds.objExists(name_custom):

            pass
        else:
            cmds.rsCreateAov(type = 'Custom', name =name_custom)
            mel.eval('redshiftUpdateActiveAovList')
            rs_name = attr_template.format(name_custom, 'name')
            cmds.rename(name_custom , name_custom)
            cmds.setAttr(rs_name, name_custom, type = 'string')
            attr_setting_c = attr_template.format(name_custom, 'exrCompression')
            cmds.setAttr(attr_setting_c, 8)
class Toon_Setup(gnc_toon_shader):
    def __init__(self, *args):
        #self.widget = {}
        self.gnc_toon_buttons()
        print('Hello, From Gary')
        self.node_triple_template = "{}.{}"
        self.node_template = "{}_{}"
        self.attr_template = "{}.{}"
    def StartUI(self, *args):
        if pm.workspaceControl( toon_window, query=True, exists=True) is False:
            pm.workspaceControl( toon_window, uiScript = self.Color_Changer(), closeCommand=self.CloseUI())
        else:
            pm.workspaceControl( toon_window, edit=True, restore=True)
    def CloseUI(self, *args):
        if pm.workspaceControl( toon_window, query=True, exists=True):
            pm.workspaceControl( toon_window, edit=True, close=True )	
    ## Button window set up Below ##
    def gnc_toon_buttons(self, *args):
        window = pm.workspaceControl(toon_window, floating=True,loadImmediately=True )
        
        
        cmds.columnLayout(adj=True, w= W, rowSpacing=spacing,  adjustableColumn=True)
        cmds.text( label='GNC TOON', fn = "boldLabelFont")
        cmds.separator(h=5, style = 'none')
        cmds.text( label='Color Attribute', bgc= [0.2, 0., .5,], h=25)

        self.color_name_input = cmds.textField(ec=self.assign_attr_geo, ann= 'Name of the Attribute you want to assign.')

        cmds.separator(h=2, style = 'none')
        self.color_selection =  cmds.colorSliderGrp(cc=self.assign_attr_geo)

        cmds.separator(h=3, style = 'none')
        cmds.paneLayout( configuration='vertical3' )
       	#self.assign_attr_geo = pm.button(label="Assign Attr", c=self.assign_attr_geo, ann= "Assign Attriube to use with Redshift_Color_Data.  You need have name in box above.")
        self.delete_attr_geo = pm.button(label="Delete Attr", c=self.delete_attr_geo, ann= "Delete createds attriube. You need have name in box above.")
        cmds.setParent('..')
        cmds.separator(h=15, style = 'doubleDash')
        # Setting the ObjectID number

        self.IDNum_id = cmds.intField(ObjectIDNum, ec=self.assign_Id,  ann= 'intField for setting the objectID number.')
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5, w=260 )
        self.assign_Id = cmds.button(label="Set ObjectID",c=self.assign_Id, ann= "Use this to assign the number in the box above to the Rs ObjectID.  You can select a group and it will change all children with a shape node.")
        cmds.separator( h = 10)
        # End of ObjectID
        cmds.columnLayout(adj=True, w= W, rowSpacing=spacing,  adjustableColumn=True  )
        cmds.separator(h=2, style = 'none')
        self.make_toonshader = cmds.button( label='Toon Shader AOVS', c=self.make_toonshader, ann= 'Select object first. This will create and assign the toon shader.  The name of the first object selected will determine the name of the shader.')
        cmds.separator(h=15, style = 'doubleDash')
        self.line_setup = cmds.button( label='Crypto Lines', c=self.create_crypto_lines, ann= 'Create cryptomattes for NodeName and RS ObjectID.  This can be used to create lines in Nuke using the cryptomatte Node. ')
        cmds.setParent( '..' )
        cmds.separator(h=4, style = 'in')
        cmds.columnLayout(adj=True, w= W, rowSpacing=spacing,  adjustableColumn=True  )      
        self.close = cmds.button( label='Close', command=('cmds.deleteUI(\"' + toon_window + '\")'), bgc= [0.45, 0, 0,]) 
        cmds.setParent( '..' )
    def assign_color(self, *args):
        
        text_field_name = cmds.textField(self.color_name_input, query=True, text=True)
        color_select = cmds.colorSliderGrp(self.color_selection, query=True, rgbValue = True)

        current_sel = cmds.ls(sl=True ) 
        sel = cmds.listRelatives(children=True, pa= True, allDescendents = True, type='mesh')
        for each in current_sel:
            node_without_shape = each.replace('Shape','')

            self.color_name = self.node_triple_template.format(node_without_shape, text_field_name, 'Color')
            print(self.color_name)
            cmds.setAttr(self.color_name, *color_select) 
    def assign_attr_geo(self, *args):
        node_template = "{}_{}"
        text_field_name = cmds.textField(self.color_name_input, query=True, text=True)
        color_select = cmds.colorSliderGrp(self.color_selection, query=True, rgbValue = True)
        
        current_select = cmds.ls(sl=True )
        sel = cmds.listRelatives(children=True, pa= True, allDescendents = True, type='mesh')
        selection = cmds.ls(sl=True)

        cmds.select(selection)
        color_name = text_field_name 
        for each in current_select:

            attr_geo_clown_pass = self.node_triple_template.format(each, text_field_name)

            #Attribute = cmds.getAttr(attr_geo_clown_pass)
            if cmds.objExists(attr_geo_clown_pass):
                #cmds.deleteAttr(attr_geo_clown_pass)
                pass
            else:
                success = False
                i = 0
                original_color_name = color_name
                color_name_red = node_template.format(color_name, 'red')
                color_name_green = node_template.format(color_name, 'green')
                color_name_blue = node_template.format(color_name, 'blue')

                cmds.addAttr( longName= color_name, usedAsColor=True, attributeType='float3' )
                cmds.addAttr( longName= color_name_red, attributeType='float', parent=color_name )
                cmds.addAttr( longName= color_name_green, attributeType='float', parent=color_name )
                cmds.addAttr( longName= color_name_blue, attributeType='float', parent=color_name )          

        print(color_select)
        
        for each in current_select:

            node_without_shape = each.replace('Shape','')
            self.color_name = self.node_triple_template.format(node_without_shape, text_field_name, 'Color')
            cmds.setAttr(self.color_name, *color_select)
    def delete_attr_geo(self, *args):

        text_field_name = cmds.textField(self.color_name_input, query=True, text=True)
        color_select = cmds.colorSliderGrp(self.color_selection, query=True, rgbValue = True)

        selection = cmds.ls(sl=True)
        sel = cmds.listRelatives(children=True, pa= True, allDescendents = True, type='mesh')

        cmds.select(selection)

        for each in selection:
            node_clown_pass = self.node_triple_template.format(each, text_field_name, 'Color')
            if cmds.objExists(node_clown_pass):
                cmds.deleteAttr(node_clown_pass)
            else:
                pass
    def create_crypto_lines(self, *args):
        # Create the cryptolines for nuke.
        # This sets up 2 cyptomattes, 1 for Node name, and one for rs objectID
        # you will need to set up the Id using the tool provided

        attr_template = "{}.{}"
        shape_template = "{}{}"
        name_custom = 'Crypto_Node'
        if cmds.objExists(name_custom):
            pass
            print(name_custom + 'already exists')
        else:
            cmds.rsCreateAov(type = 'Cryptomatte', name =name_custom)
            mel.eval('redshiftUpdateActiveAovList')
            rs_name = attr_template.format(name_custom, 'name')
            cmds.rename(name_custom , name_custom)
            cmds.setAttr(rs_name, name_custom, type = 'string')


        name_custom_b = 'Crypto_RS_ID'
        if cmds.objExists(name_custom_b):
            pass
            print(name_custom_b + 'already exists')
        else:
            cmds.rsCreateAov(type = 'Cryptomatte', name =name_custom_b)
            mel.eval('redshiftUpdateActiveAovList')
            rs_name = attr_template.format(name_custom_b, 'name')
            cmds.rename(name_custom_b , name_custom_b)
            cmds.setAttr(rs_name, name_custom_b, type = 'string')

            # change name of AOVs for the toon shaders
            attr_setting_a = attr_template.format(name_custom_b, 'idType')
            cmds.setAttr(attr_setting_a, 2)
    def assign_Id(self, *args):
        
        self.IDNum_id = cmds.intField( ObjectIDNum, query=True, value=True)
        
        currentSelection = cmds.ls(sl=True ) 
        sel = cmds.listRelatives(children=True, pa= True, allDescendents = True, type='mesh')
        for each in sel:
            #IDNum2 = cmds.intField(IDNum, query=True)
            objectId = each + '.rsObjectId'
            #print IDNum2
            getattr = cmds.getAttr(objectId)
            #print getattr
            
            cmds.setAttr(objectId, self.IDNum_id)

        print('Changed ObjectID',currentSelection, 'to ', self.IDNum_id)
