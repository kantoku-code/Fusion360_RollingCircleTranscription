#FusionAPI_python_Addin RollingCircleTranscription
#Author-kantoku
#Description-

#using Fusion360AddinSkeleton
#https://github.com/tapnair/Fusion360AddinSkeleton
#Special thanks:Patrick Rainsberry

from .RCT_View import RCT_View

commands = []
command_definitions = []

# command
cmd = {
    'cmd_name': 'Rolling Circle Transcription',
    'cmd_description': 'It transfers the shape by two circular motions.',
    'cmd_id': 'rct_f360_solid',
    'cmd_resources': './resources/command',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidCreatePanel',
    'class': RCT_View
}
command_definitions.append(cmd)

cmd = {
    'cmd_name': 'Rolling Circle Transcription',
    'cmd_description': 'It transfers the shape by two circular motions.',
    'cmd_id': 'rct_f360_surf',
    'cmd_resources': './resources/command',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SurfaceCreatePanel',
    'class': RCT_View
}
command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False

# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)

def run(context):
    for run_command in commands:
        run_command.on_run()

def stop(context):
    for stop_command in commands:
        stop_command.on_stop()