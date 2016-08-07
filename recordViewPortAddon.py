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
        col = layout.column(align=True)
        col.operator("object.recorder", text="Record", icon='MOD_SMOOTH')
        # col.operator("object.recorder_stop", text="Stop", icon='MOD_SMOOTH')
        col.label("(Escape to stop)")

class RecorderStop(bpy.types.Operator):
    bl_idname = "object.recorder_stop"
    bl_label = 'Viewport Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    index = 0
    record = True

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        Recorder.record = False



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
        cmd = '~/dev/py/recordViewport/ffmpeg -framerate 25 -i '+bpy.context.scene.render.filepath+'recorder-viewport-pic%d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p '+bpy.context.scene.render.filepath+'output.mp4'
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
