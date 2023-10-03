import bpy

class SEQUENCER_OT_adjust_volume(bpy.types.Operator):
    bl_idname = "sequencer.adjust_volume"
    bl_label = "Adjust Audio Volume"

    direction: bpy.props.EnumProperty(
        items=[('UP', "Up", "Increase volume"), ('DOWN', "Down", "Decrease volume")],
        name="Direction",
        description="Increase or decrease volume",
        default="UP"
    )

    volume_change: bpy.props.FloatProperty(
        name="Volume Change",
        description="Amount to change the volume",
        default=0.2,
        min=0.0,
        soft_min=0.0,
        step=0.2
    )

    @classmethod
    def poll(cls, context):
        return (
            context.area.type == 'SEQUENCE_EDITOR' and
            context.selected_sequences is not None and
            all(strip.type == 'SOUND' for strip in context.selected_sequences)
        )

    def execute(self, context):
        if self.direction == "UP":
            volume_change = self.volume_change
        else:
            volume_change = -self.volume_change

        for strip in context.selected_sequences:
            if strip.type == 'SOUND':
                strip.volume += volume_change

        return {'FINISHED'}


class SEQUENCER_OT_volume_popup(bpy.types.Operator):
    bl_idname = "sequencer.volume_popup"
    bl_label = "Volume"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if (
            context.scene and
            context.scene.sequence_editor and
            context.scene.sequence_editor.active_strip
        ):
            return context.scene.sequence_editor.active_strip.type == 'SOUND'
        else:
            return False

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=170)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        strip = context.scene.sequence_editor.active_strip
        layout = self.layout
        layout.use_property_decorate = True
        layout.prop(strip, "volume", text="Volume")


def menu_func(self, context):
    layout = self.layout
    layout.operator(SEQUENCER_OT_adjust_volume.bl_idname, text="Adjust Audio Volume")
    layout.menu("SOUND_MT_adjust_volume_submenu")


class SEQUENCER_MT_sound_menu(bpy.types.Menu):
    bl_idname = "SOUND_MT_adjust_volume_submenu"
    bl_label = "Sound"

    def draw(self, context):
        layout = self.layout
        layout.operator(SEQUENCER_OT_volume_popup.bl_idname, text="Volume")
        layout.separator()
        prop = layout.operator(SEQUENCER_OT_adjust_volume.bl_idname, text="Volume Down")
        prop.direction = "DOWN"
        prop = layout.operator(SEQUENCER_OT_adjust_volume.bl_idname, text="Volume Up")
        prop.direction = "UP"


def register():
    bpy.utils.register_class(SEQUENCER_OT_adjust_volume)
    bpy.utils.register_class(SEQUENCER_MT_sound_menu)
    bpy.types.SEQUENCER_MT_strip.append(menu_func)
    bpy.types.SEQUENCER_MT_context_menu.append(menu_func)
    bpy.utils.register_class(SEQUENCER_OT_volume_popup)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="Sequencer", space_type="SEQUENCE_EDITOR")
    
    kmi = km.keymap_items.new(SEQUENCER_OT_adjust_volume.bl_idname, type='EQUAL', value='PRESS', ctrl=True, repeat = True)
    kmi.properties.direction = "UP"    
    
    kmi = km.keymap_items.new(SEQUENCER_OT_adjust_volume.bl_idname, type='PLUS', value='PRESS', ctrl=True, repeat = True)
    kmi.properties.direction = "UP"
  
    kmi = km.keymap_items.new(SEQUENCER_OT_adjust_volume.bl_idname, type='MINUS', value='PRESS', ctrl=True, repeat = True)
    kmi.properties.direction = "DOWN"

    kmi = km.keymap_items.new(SEQUENCER_OT_volume_popup.bl_idname, type='V', value='PRESS')

def unregister():
    bpy.utils.unregister_class(SEQUENCER_MT_sound_menu)
    bpy.utils.unregister_class(SEQUENCER_OT_adjust_volume)
    bpy.utils.unregister_class(SEQUENCER_OT_volume_popup)
    
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.get("Sequencer")
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == SEQUENCER_OT_adjust_volume.bl_idname or kmi.idname == SEQUENCER_OT_volume_popup.bl_idname:
                km.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()
