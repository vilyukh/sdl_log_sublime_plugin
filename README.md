# sdl_sublime_log_plugin
Sublime Text plugin  for handy work with SdlLogs.

## Requirements
This plugin requires at least Sublime Text 3 v.3176 or higher for best performance and correct syntax

## Installing
- Move directory "SdlLogs" to Sublime Packages folder.
(Generally at /home/*USER*/.config/sublime-text-3/Packages)
- Change syntax in Sublime to SdlLogs.
(View -> Syntax ->SdlLogs)

## Dependencies
- Should install package for yaml
(Enter in terminal 'sudo apt-get install python-yaml')

## Functionality
This plugin implements color scheme and simple commands to work with SdlLogs
- Indicates methods and make them clickable (Opens file containing that method and highlight him)
- Search for common syntax patterns and highlight them (color scheme)
- Implements commands for filtering columns&strings, finding not closed functions

## Configuration
Open Sublime in top panel choose preferences->Package->Settings->SdlLogs:
- Item "Color Scheme" contain configuration for text color.
- Item "Setting" contain all path to configure files and path to your sources if logs exists incorrect absolute path to file.
- Item "Key Bindings" contain all keybindings configuration.
