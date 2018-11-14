# sdl_sublime_log_plugin
Sublime Text plugin  for handy work with SdlLogs.

## Installation

### Requirements
This plugin requires at least Sublime Text 3 v.3176 or higher for best performance and correct syntax

Install YAML:  

    sudo apt-get install python-yaml 

### How to install sdl_sublime_log_plugin:
1. Clone this repository. If you have downloaded project as like archive, you have to unpacked it.
2. Copy "SdlLogs" folder to Sublime Packages folder.
(Generally at /home/*USER*/.config/sublime-text-3/Packages)
3. Change syntax in Sublime to SdlLogs.
(View -> Syntax ->SdlLogs)

## Working with sdl_sublime_log_plugin

### Configuration

Open Sublime in top panel choose preferences->Package->Settings->SdlLogs:

1. Item "Color Scheme" contain configuration for text color.
2. Item "Setting":
    - `"color_scheme"` path to color configuration file.
    - `"syntax"` path to syntax configuration file.
    - `"extensions"` contain file extensions with which the plugin works.
    - `"source_path"` path to your source code directory (need for work recursive search)
    - `"check_keys_override"` responsible flag for turn on/off 'Key bindings override' function.
3. Item "Key Bindings" contains all keybindings configuration.

### Jump to file
Move mouse cursor to line you interested in, which contains path of source file and press `"F12"` (by default). Will be opened new separate tab with source code and mouse cursor will be moved to line in code which has generated log.

### Key bindings override
After each starting sublime, plugin check key bindings override with other plugin, default and user key bindings. 
If such exist will show message with problem key bindings and open key binding settings. You can turn off this function change `check_keys_override` tag value in setting file to false.

### Show/hide by columns 
Shortcut for show/hide by columns:
1. `"alt+1"` - date.
2. `"alt+2"` - thread address.
3. `"alt+3"` - extra path.
4. `"alt+4"` - component.

### Function Call Command
This command highlight functions which doesn't have exit in current .log fileHow to:
1. Press `"alt+6"` if used default plugin keymap (or key linked with 'function_call')

### Function Tree Command
This command creates file with call tree for selected function.
How to use:
1. Select function name
2. Press `"alt+7"` if you use default plugin keymap (or key linked with 'function_tree')

### Ignition Cycle
This event automatically adds separator before every ignition cycle.

### Filter By Value
This command sorts with clipping file by selected text.

How to use:
1. Select text
2. Press `"alt+5"` if you use default plugin keymap (or key linked with 'filter_by_value')
 
