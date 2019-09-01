import json

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

# global set of event handlers to keep them referenced for the duration of the command
_handlers = []
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_host = 'js/index.html'  # "http://localhost"
_use_new_browser = True
_palette_id = 'myPaletteId'
_palette_name = 'My Palette'
_palette_width = 600
_palette_height = 600
_command_id = 'showPaletteId'
_command_name = 'Show Palette'
_command_tooltip = 'Show Palette description'
_command_resource_folder = ''
_toolbar_id = 'SolidScriptsAddinsPanel'


# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global _host, _use_new_browser
        try:
            # Create and display the palette.
            palette = _ui.palettes.itemById(_palette_id)
            if not palette:
                palette = _ui.palettes.add(_palette_id, _palette_name, _host, True, True, True, _palette_width,
                                           _palette_height, _use_new_browser)

                # Dock the palette to the right side of Fusion window.
                palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

                # Add handler to HTMLEvent of the palette.
                on_html_event = MyHTMLEventHandler()
                palette.incomingFromHTML.add(on_html_event)
                _handlers.append(on_html_event)

                # Add handler to CloseEvent of the palette.
                on_closed = MyCloseEventHandler()
                palette.closed.add(on_closed)
                _handlers.append(on_closed)
            else:
                palette.isVisible = True
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            command = args.command
            on_execute = ShowPaletteCommandExecuteHandler()
            command.execute.add(on_execute)
            _handlers.append(on_execute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        # Event handler for the commandExecuted event.


class MyCloseEventHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            return
        except:
            pass


# Event handler for the palette HTML event.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            html_args = adsk.core.HTMLEventArgs.cast(args)
            data = json.loads(html_args.data)
            if 'id' in data.keys() and 'name' in data.keys():
                args.returnData = str({"id": data['id'], "name": data['name']})
        except:
            pass


def run(context):
    try:
        global _ui, _app, _command_id, _command_name, _command_resource_folder, _command_tooltip
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Add a command that displays the panel.
        show_palette_cmd_def = _ui.commandDefinitions.itemById(_command_id)
        if not show_palette_cmd_def:
            show_palette_cmd_def = _ui.commandDefinitions.addButtonDefinition(_command_id, _command_name,
                                                                              _command_tooltip,
                                                                              _command_resource_folder)
            # Connect to Command Created event.
            on_command_created = ShowPaletteCommandCreatedHandler()
            show_palette_cmd_def.commandCreated.add(on_command_created)
            _handlers.append(on_command_created)

        # Add the command to the toolbar.
        panel = _ui.allToolbarPanels.itemById(_toolbar_id)
        control = panel.controls.itemById(_command_id)
        if not control:
            panel.controls.addCommand(show_palette_cmd_def)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        global _toolbar_id, _command_id, _palette_id
        # Delete the palette created by this add-in.
        palette = _ui.palettes.itemById(_palette_id)
        if palette:
            palette.deleteMe()

        # Delete controls and associated command definitions created by this add-ins
        panel = _ui.allToolbarPanels.itemById(_toolbar_id)
        cmd = panel.controls.itemById(_command_id)
        if cmd:
            cmd.deleteMe()
        cmd_def = _ui.commandDefinitions.itemById(_command_id)
        if cmd_def:
            cmd_def.deleteMe()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
