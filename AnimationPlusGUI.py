import bpy

# Select the material you want to modify
material_name = "Material"  # Change this to your material name
material = bpy.data.materials.get(material_name)

def revert_to_original(material):
    # Find and delete the added nodes
    nodes_to_remove = []
    for node in material.node_tree.nodes:
        if node.type in {'MIX_SHADER', 'BSDF_TRANSPARENT', 'MAPPING', 'TEX_COORD', 'SEPARATE_XYZ'}:
            nodes_to_remove.append(node)
    for node in nodes_to_remove:
        material.node_tree.nodes.remove(node)

    # Find Material Output node
    material_output = None
    for node in material.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            material_output = node
            break

    # Connect Principal BSDF to Material Output Surface
    principal_bsdf = None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principal_bsdf = node
            break
    if material_output and principal_bsdf:
        material.node_tree.links.new(principal_bsdf.outputs[0], material_output.inputs[0])

def create_animation(revert_back=False):
    # Your script for creating animation goes here
    if revert_back:
        revert_to_original(material)
    else:
        if material:
            # Flag to determine whether to revert to original state
            revert_back = False

            # If flag is set to True, revert to original state
            if revert_back:
                revert_to_original(material)
            else:
                bpy.context.object.active_material.blend_method = 'BLEND'
                bpy.context.object.active_material.use_backface_culling = True
                # Create Mix Shader node
                mix_shader = material.node_tree.nodes.new('ShaderNodeMixShader')
                mix_shader.location = (0, 200)

                # Create Transparent BSDF node
                transparent_bsdf = material.node_tree.nodes.new('ShaderNodeBsdfTransparent')
                transparent_bsdf.location = (-200, 200)

                # Link Transparent BSDF to second input of Mix Shader
                material.node_tree.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])

                # Connect existing Principal BSDF to first input of Mix Shader
                principal_bsdf = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principal_bsdf = node
                        break
                if principal_bsdf:
                    material.node_tree.links.new(principal_bsdf.outputs[0], mix_shader.inputs[2])

                # Create Mapping node
                mapping = material.node_tree.nodes.new('ShaderNodeMapping')
                mapping.location = (-400, 0)
                
                # Set initial keyframe for Mapping node's Location X value
                mapping.inputs[1].default_value[0] = -2
                mapping.inputs[1].keyframe_insert(data_path="default_value", index=0, frame=0)

                # Create Texture Coordinate node
                tex_coord = material.node_tree.nodes.new('ShaderNodeTexCoord')
                tex_coord.location = (-600, 0)

                # Connect Texture Coordinate to Mapping node
                material.node_tree.links.new(tex_coord.outputs[0], mapping.inputs[0])

                # Create Separate XYZ node
                separate_xyz = material.node_tree.nodes.new('ShaderNodeSeparateXYZ')
                separate_xyz.location = (-200, -200)

                # Connect Mapping node to Separate XYZ node
                material.node_tree.links.new(mapping.outputs[0], separate_xyz.inputs[0])

                # Connect Separate XYZ to Mix Shader factor
                material.node_tree.links.new(separate_xyz.outputs[0], mix_shader.inputs['Fac'])

                # Find Material Output node
                material_output = None
                for node in material.node_tree.nodes:
                    if node.type == 'OUTPUT_MATERIAL':
                        material_output = node
                        break

                # Link Mix Shader output to Material Output Surface
                if material_output:
                    material.node_tree.links.new(mix_shader.outputs[0], material_output.inputs[0])

                # Keyframe Mapping node's Location X value at frame 40
                mapping.inputs[1].default_value[0] = 2
                mapping.inputs[1].keyframe_insert(data_path="default_value", index=0, frame=40)

                # Select the Mix Shader node
                material.node_tree.nodes.active = mix_shader
        else:
            print("Material not found.")


class SimpleOperator(bpy.types.Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Simple Operator"

    action: bpy.props.StringProperty()

    def execute(self, context):
        if self.action == 'create_animation':
            create_animation(revert_back=False)
        elif self.action == 'remove_animation':
            create_animation(revert_back=True)
        return {'FINISHED'}


class SimplePanel(bpy.types.Panel):
    bl_label = "Animation Tools"
    bl_idname = "OBJECT_PT_animation_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.simple_operator", text="Create Animation").action = 'create_animation'

        row = layout.row()
        row.operator("object.simple_operator", text="Remove Animation").action = 'remove_animation'


def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(SimplePanel)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_class(SimplePanel)


if __name__ == "__main__":
    register()
