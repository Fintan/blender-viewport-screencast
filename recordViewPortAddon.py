bl_info = {
    "name": "Record Viewport",
    "description": "Simple Viewport recording using OpenGl quick render and ffmpeg.",
    "author": "Fintan Boyle",
    "version": (0, 1, 0),
    "blender": (2, 7, 6),
    "location": "View 3D > Tool Shelf",
    "warning": "WIP", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "https://github.com/fintan/Blender-Viewport-Recorder/issues",
    "support": "COMMUNITY",
    "category": "3D View"
    }

import bpy
import os
from bpy.props import *
 
#
#    Store properties in the active scene
#
def initSceneProperties(scn):
    # bpy.types.Scene.MyInt = IntProperty(
    #     name = "Integer", 
    #     description = "Enter an integer")
    # scn['MyInt'] = 17
 
    # bpy.types.Scene.MyFloat = FloatProperty(
    #     name = "Float", 
    #     description = "Enter a float",
    #     default = 33.33,
    #     min = -100,
    #     max = 100)
 
    bpy.types.Scene.ViewContextBool = BoolProperty(
        name = "Use 3D View", 
        description = "True or False?")
    scn['MyBool'] = True
 
    bpy.types.Scene.ViewContextEnum = EnumProperty(
        items = [('3D view', 'Un', 'One'), 
                 ('Scene settings', 'Deux', 'Two')],
        name = "Context")
    scn['ViewContextEnum'] = 0
 
    bpy.types.Scene.SaveNameStr = StringProperty(
        name = "File name")
    scn['SaveNameStr'] = "recording-of-viewport"
    return
 
initSceneProperties(bpy.context.scene)

class FastOpenGlRecordPanel(bpy.types.Panel):
    bl_idname = "object.fast_open_gl_record_panel"
    bl_label = 'Viewport Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(self, context):
        return bpy.context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        col.operator("object.recorder", text="Record", icon='MOD_SMOOTH')
        col.label("(Escape to stop)")
        layout.prop(scn, 'ViewContextBool', icon='BLENDER', toggle=True)
        layout.prop(scn, 'ViewContextEnum')
        layout.prop(scn, 'SaveNameStr')
        # col.operator("object.recorder_stop", text="Stop", icon='MOD_SMOOTH')


class Recorder(bpy.types.Operator):
    bl_idname = "object.recorder"
    bl_label = 'Viewport Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    index = 0

    _timer = None

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            bpy.context.scene.frame_set(2)
            Recorder.index += 1;
            filepath = bpy.context.scene.render.filepath
            bpy.context.scene.render.filepath += 'recorder-viewport-pic' + str(Recorder.index)
            bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)
            bpy.context.scene.render.filepath = filepath

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        cmd = 'ffmpeg -framerate 25 -i '+bpy.context.scene.render.filepath+'recorder-viewport-pic%d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p '+bpy.context.scene.render.filepath+'output.mp4'
        # cmd = '~/dev/py/recordViewport/ffmpeg -framerate 25 -i '+bpy.context.scene.render.filepath+'recorder-viewport-pic%d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p '+bpy.context.scene.render.filepath+'output.mp4'
        os.system(cmd)
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(FastOpenGlRecordPanel)
    bpy.utils.register_class(Recorder)
    bpy.utils.register_class(RecorderStop)

def unregister():
    bpy.utils.unregister_class(FastOpenGlRecordPanel)
    bpy.utils.unregister_class(Recorder)
    bpy.utils.unregister_class(RecorderStop)
