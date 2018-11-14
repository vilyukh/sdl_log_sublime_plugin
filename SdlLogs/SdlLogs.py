import sublime
import sublime_plugin
import json
import re
import os
from os import walk
from os import path
import fnmatch
import shutil
import zipfile
import yaml


class SettingsTags:
    """
    Contains useful attributes from settings file.

    Attributes
    ----------
    NAME : const str
        Name of plugin.
    EXTENTION : const str
        Extention of plugin settings file.
    SOURCE_PATH : const str
        Name settings attribute.
    PACKAGE_EXTENTION : const str
        Extention of plugins.
    CHECK_KEYS_OVERRIDE : const str
        Name settings attribute.
    """
    NAME = "SdlLogs"
    EXTENTION = ".sublime-settings"
    SOURCE_PATH = "source_path"
    PACKAGE_EXTENTION = ".sublime-package"
    CHECK_KEYS_OVERRIDE = "check_keys_override"


class KeyMapRegex:
    """
    Contains useful attributes from settings file.

    Attributes
    ----------
    PLUGIN_KEY_MAP : const str
        Key map for plugin.
    USER_KEY_MAP : const str
        User key map.
    DEFAULT_KEY_MAP : const str
        Default key map.
    BASE_FILE : const str
        Base key map for plugin.
    OVERRIDE_MESSAGE : const str
        Message when has overriding.
    IGNORE_OVERRIDING_MESSAGE : const str
        Message when ignored overriding.
    """

    PLUGIN_KEY_MAP = "Packages/SdlLogs/Default (Linux).sublime-keymap"
    USER_KEY_MAP = "Packages/User/Default (Linux).sublime-keymap"
    DEFAULT_KEY_MAP = "Packages/Default/Default (Linux).sublime-keymap"
    BASE_FILE = "${packages}/SdlLogs/Default (${platform}).sublime-keymap"
    OVERRIDE_MESSAGE = 'This {0} key binding to function "{1}" can be override of "{2}" from plugin "{3}" or on the contrary\n'
    IGNORE_OVERRIDING_MESSAGE = " \
        Check key binding overriding was ignored \
    "

    def __init__(self):
        self.plugin_keybindigs = list()
        self.user_keybindigs = list()
        self.need_open_settings = False
        self.opened_settings = False
        self.need_to_check = False
        self.messages_override = list()

    def open_settings_window(self):

        sublime.run_command(
            'edit_settings',
            {"base_file": self.BASE_FILE,
             "default": "[\\n\\t$0\\n]\\n"}
        )

    def check_override(self, keybindigs, name_plugin):
        """
        Check overriding between plugin keys and `keybindigs`.
        Show message if found overriding.
        Opening settings window will be done with delay `3 seconds`.

        Arguments
        ----------
            keybindigs : list
                other key bindings
        """
        for plugin_key in self.plugin_keybindigs:
            for other_key in keybindigs:
                if str(plugin_key[1]).strip() == str(other_key[1]).strip():
                    self.messages_override.append(
                        self.OVERRIDE_MESSAGE.format(
                            plugin_key[1],
                            plugin_key[2],
                            other_key[2],
                            name_plugin
                        )
                    )
                    self.need_open_settings = True
        self.messages_override.append("\n")
        if not self.opened_settings and self.need_open_settings:
            self.opened_settings = True
            sublime.set_timeout(self.open_settings_window, 3000)

    def check_overriding_if_enable(self):
        """
        Check overriding if `SettingsTags.CHECK_KEYS_OVERRIDE` is true.
        Show message if false.
        """
        do_check = sublime.load_settings(SettingsTags.NAME +
                                         SettingsTags.EXTENTION).get(
            SettingsTags.CHECK_KEYS_OVERRIDE)

        if do_check:
            self.check_overriding()
            if self.messages_override:
                view = sublime.active_window().new_file()
                message = "".join(self.messages_override)
                view.run_command("writer", {"message": message})
                view.set_name("key bindings overriding")
        else:
            sublime.active_window().status_message(
                self.IGNORE_OVERRIDING_MESSAGE
            )

    def check_overriding(self):
        """
        Check key binding overriding plugin with:
            - sublime.installed_packages_path
                other plugins keybindigs
            - user/default
                user/default keybindigs in sublime
        """
        default_keymap = sublime.load_resource(KeyMapRegex.DEFAULT_KEY_MAP)
        default_keys = re.findall(
            syntax.key_value_command, default_keymap)

        self.load_plugin_keybindigs()
        self.check_override(default_keys, self.DEFAULT_KEY_MAP)

        for file in os.listdir(sublime.installed_packages_path()):

            if str(file).find(SettingsTags.PACKAGE_EXTENTION) != -1:
                zip_ = zipfile.ZipFile(
                    path.join(sublime.installed_packages_path(), file))
                arr_keys = []
                arr_keys.extend(
                    filter(lambda file_name:
                           re.search(syntax.key_map,
                                     str(file_name)),
                           zip_.namelist()))

            for item in arr_keys:
                temp_keys = re.findall(
                    syntax.key_value_command, str(
                        zip_.open(item).read()))
                self.check_override(temp_keys, file)

    def load_plugin_keybindigs(self):
        """
        Load user and plugin key maps.
        """
        user_keymap = sublime.load_resource(KeyMapRegex.USER_KEY_MAP)
        plugin_keymap = sublime.load_resource(KeyMapRegex.PLUGIN_KEY_MAP)

        user_keybindigs = re.findall(
            syntax.key_value_command, user_keymap)
        plugin_keybindigs = re.findall(
            syntax.key_value_command, plugin_keymap)

        for user_key in range(len(user_keybindigs)):
            for plugin_key in range(len(plugin_keybindigs)):

                if str(plugin_keybindigs[plugin_key][2]).strip() == str(user_keybindigs[user_key][2]).strip():
                    list_ = list(plugin_keybindigs[plugin_key])
                    list_[1] = user_keybindigs[user_key][1]
                    plugin_keybindigs[plugin_key] = tuple(list_)

        self.plugin_keybindigs = plugin_keybindigs
        self.user_keybindigs = user_keybindigs


class WriterCommand(sublime_plugin.TextCommand):
    def run(self, edit, message):
        self.view.insert(edit, 0, message)


class LogSyntax:
    """
    Contains regular expretion which parsed from yaml file.

    Attributes
    ----------
    NAME : const str
        Name of syntax attribute in settings file.
    Tags : class Tags
        Contains name of attributes in yaml file.

    Methods
    -------
    load_syntax(self, pathToSettings)
        Load regular expression from yaml file.

    """
    NAME = "syntax"

    class Tags:
        """
        Contains name of attributes in yaml file.
        """
        VARIABLES = "variables"
        DATE_TIME = "date_time"
        ID = "id"
        COMPONET = "component"
        PATH = "path"
        LINE = "line"
        MESSAGE = "message"
        JUNK = "junk"
        THREAD_ENTER  = "thread_enter"
        THREAD_EXIT   = "thread_exit"
        THREAD        = "thread"
        MSG_STRING    = "msg_string"
        BORDER_STRING = "border_string"
        APP_MARK      = "app_mark"
        KEY_VALUE_COMMAND = "key_value_command"
        KEY_MAP = "key_map"

    def __init__(self):
        self.date_time = ""
        self.id = ""
        self.component = ""
        self.path = ""
        self.line = ""
        self.message = ""
        self.junk = ""
        self.thread_enter = ""
        self.thread_exit = ""
        self.msg_string    = ""
        self.border_string = ""
        self.app_mark      = ""
        self.key_value_command = ""
        self.key_map = ""

    def load_syntax(self, pathToSettings):
        """
        Load regular expression from yaml file.
        Search pattern for load syntax:
            Order regular expression in yaml file should as:
                variables:
                    name_regex: some_regex
                    ...
        Args:
            pathToSettings : str
                path to setting file
        """
        obj = sublime.load_settings(pathToSettings).get(self.NAME)

        if not obj:
            sublime.error_message("Absent path to syntax file")
        else:
            yaml_file = yaml.load(sublime.load_resource(obj))
            regex = yaml_file[self.Tags.VARIABLES]
            self.date_time = regex[self.Tags.DATE_TIME]
            self.id = regex[self.Tags.ID]
            self.component = regex[self.Tags.COMPONET]
            self.path = regex[self.Tags.PATH]
            self.line = regex[self.Tags.LINE]
            self.message = regex[self.Tags.MESSAGE]
            self.junk = regex[self.Tags.JUNK]
            self.thread_enter = regex[self.Tags.THREAD_ENTER]
            self.thread_exit = regex[self.Tags.THREAD_EXIT]
            self.msg_string = regex[self.Tags.MSG_STRING]
            self.border_string = regex[self.Tags.BORDER_STRING]
            self.app_mark = regex[self.Tags.APP_MARK]
            self.thread = regex[self.Tags.THREAD]
            self.key_value_command = regex[self.Tags.KEY_VALUE_COMMAND]
            self.key_map = regex[self.Tags.KEY_MAP]


def get_selected_text(self):
    """
    Return selected text from view.

    Parameters
    ----------
    self : class view

    Returns
    ----------
    str
        Selected text
    """
    sel_text = self.view.sel()
    sel_text = self.view.substr(sel_text[0])
    return sel_text


def hide_show_region(self, pattern):
    """
    Hide or show region by pattern. Show if all regions is hidden and for hide, safe logic

    Parameters
    ----------
    self : class view
    pattern: str
    """
    trc_regions = self.view.find_all(pattern)
    if not self.view.fold(trc_regions):
        self.view.unfold(trc_regions)


def open_file(self, path_to_file, line, message_if_absent):
    """
    Open file and jump to line in opened file. Show message if file not found

    Parameters
    ----------
    self : class view
    path_to_file : str
    line : integer
    message_if_absent : str
    """

    if path.isfile(path_to_file):
        self.view.window().open_file(path_to_file + ":" + line, sublime.ENCODED_POSITION)
    else:
        sublime.error_message(message_if_absent)


class HideDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        hide_show_region(self, syntax.date_time)


class FunctionCallCommand(sublime_plugin.TextCommand):
    """
        Highlight function which doesn't have exit
    """

    def run(self, edit):
        pos_fatal = 0
        enter_regex = "initial fake value"
        result_array = []
        while enter_regex:
            enter_region = self.view.find(syntax.thread_enter, pos_fatal)
            enter_regex = self.view.substr(enter_region)
            enter_regex = enter_regex[enter_regex.find(" ")+1:]
            enter_regex = enter_regex[:enter_regex.find(": ")+1]
            if enter_regex:
                exit_region = self.view.find(
                    enter_regex + syntax.thread_exit, pos_fatal)
                if exit_region.size() is not 0:
                    pos_fatal = enter_region.b
                else:
                    enter_region.a += 8
                    self.view.show(enter_region)
                    result_array.append(enter_region)
                    pos_fatal = enter_region.b
        self.view.add_regions('func_call', result_array,
                              'param.func_call.SDL_Logs')


class HideThreadAddressCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        hide_show_region(self, syntax.id)


class HideComponentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        hide_show_region(self, syntax.component)


class HideExtraPathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        hide_show_region(self, syntax.junk)


class FilterByValueCommand(sublime_plugin.TextCommand):
    """
        Clipping all strings which contain selected text
    """
    def run(self, edit, ext_value):
        """
            Parameters
            ----------
            self : Sublime Window Class
            edit : Sublime Edit Class
            ext_value: indicates string for clipping and target window
        """
        sel_text_regex = get_selected_text(self)
        if ext_value != "this_window":
            sel_text_regex = ext_value
        if sel_text_regex != "":
            trc_regions = self.view.find_all(sel_text_regex)
            active_window = sublime.active_window()
            left_border = 0
            for i in range (0, len(trc_regions)):
                trc_regions[i] = self.view.full_line(trc_regions[i])
                trc_regions[i] = self.view.substr(trc_regions[i])

            if ext_value != "this_window":
                active_window.new_file()
            else:   
                self.view.erase(edit, sublime.Region(0, self.view.size()))
            view = active_window.active_view()
            for region in trc_regions:
                left_border+= view.insert(edit, left_border, region)


class JumpToFileCommand(sublime_plugin.TextCommand):
    """
        Represents go to file.
    """

    def run(self, edit):
        """
            Read path from line and check validity it.
            There are to case go to file:
                there is value in 'source_path' attribute in settings file
                there isn't value in 'source_path' attribute in settings file
        """

        ERROR_MESSAGE = "File '{0}' not found. Maybe path to source files " \
                        "in your settings is incorrect or file really absent"

        SDL_LOG_SOURCE = "/sdl_core/src/"

        FILE_NAME_WITHOUT_PATH_NAME = "(.+)(/|(] +))(.{0,}\\.(c|cc|h|cpp|hpp)):(\\d{1,})"
        FULL_PATH_FILE = "(/.*)(/sdl_core/src/.{0,}\\.(c|cc|h|cpp|hpp)):(\\d{1,})"

        # Check exist file in directory
        # file in directory have
        primaryPath_exist = re.search(
            FULL_PATH_FILE, self.view.substr(self.view.line(self.view.sel()[0])))
        # file in directory haven't
        path_not_exist = re.search(FILE_NAME_WITHOUT_PATH_NAME, self.view.substr(
            self.view.line(self.view.sel()[0])))

        if primaryPath_exist:
            path_to_file = primaryPath_exist.group(
                1) + primaryPath_exist.group(2)

            if path.isfile(path_to_file):
                line = primaryPath_exist.group(4)
                open_file(self, path_to_file, line,
                          ERROR_MESSAGE.format(path_to_file))
            else:
                path_to_file = self.view.settings().get(SettingsTags.SOURCE_PATH) + \
                    primaryPath_exist.group(2)
                line = primaryPath_exist.group(4)

                open_file(
                    self, path_to_file, line, ERROR_MESSAGE.format(path_to_file))
        else:
            # Check option sourcePath empty or not
            if self.view.settings().get(SettingsTags.SOURCE_PATH):
                flagFind = False
                file_name = path_not_exist.group(4)
                path_to_file = self.view.settings().get(
                    SettingsTags.SOURCE_PATH) + SDL_LOG_SOURCE

                for root, dirnames, filenames in walk(path_to_file):
                    for filename in fnmatch.filter(filenames, file_name):
                        if filename:
                            flagFind = True
                            path_to_file = root + '/' + filename
                            line = path_not_exist.group(5)

                            open_file(self, path_to_file, line,
                                      ERROR_MESSAGE.format(path_to_file))
                            break
                if not flagFind:
                    sublime.error_message(
                        ERROR_MESSAGE.format(file_name))
            else:
                file_name = path_not_exist.group(4)
                sublime.error_message(
                    ERROR_MESSAGE.format(file_name))


class FunctionTreeCommand(sublime_plugin.TextCommand):
    """
        Represents function tree
    """
    def run(self, edit):
        pos = 0
        deep_counter = 1
        sel_text_regex = self.view.sel()[0]
        if sel_text_regex.size() != 0:
            sel_text_regex = self.view.full_line(sel_text_regex)
            sel_text_regex = self.view.find(syntax.thread[2:-1], sel_text_regex.begin())
            sel_text_regex = self.view.substr(sel_text_regex)
            self.view.run_command('filter_by_value', {'ext_value': sel_text_regex})
            active_window = sublime.active_window()
            view = active_window.active_view()
            region = view.find(sel_text_regex, pos)
            while region != sublime.Region(-1,-1):
                region = view.full_line(region)
                trc_string = view.substr(region)
                for i in range (0,deep_counter):
                    view.insert(edit, region.begin(), "     ")
                pos = region.end()+deep_counter*5
                if trc_string.find(syntax.thread_enter) != -1:
                    deep_counter+=1
                elif trc_string.find(syntax.thread_exit) != -1:
                    deep_counter-=1  
                region = view.find(sel_text_regex, pos)


class IgnCycleListener(sublime_plugin.ViewEventListener):
    """
        On log file loaded:
        Creates separator in text for every ignition cycle 
    """
    def on_load(self):
        file_name = self.view.file_name()
        if (file_name.find(".log")!= -1):
            pos = 0
            app_region=self.view.find(syntax.app_mark, pos)
            while app_region != sublime.Region(-1,-1):
                full_line = self.view.full_line(app_region)
                if full_line.begin() == 0:
                    full_line.b = full_line.a
                else:
                    full_line.a-=1
                    full_line.b = full_line.a
                    full_line = self.view.full_line(full_line)
                border_line = full_line
                full_line = self.view.substr(full_line)
                if full_line.find("===") == -1:
                    self.view.run_command("text_insert", {'end_pos': border_line.end()})
                pos = self.view.find(syntax.app_mark, pos)
                pos = pos.end()
                app_region=self.view.find(syntax.app_mark, pos)


class TextInsertCommand(sublime_plugin.TextCommand):
    """
        Inserts text in current file
    """
    def run(self, edit, end_pos):
        """
        end_pos: position for insert
        """
        self.view.insert(edit, end_pos, syntax.border_string+"\n"+syntax.msg_string+"\n"+syntax.border_string+"\n")


syntax = LogSyntax()


def plugin_loaded():
    """
    This function will be call when plugin is loaded
    """
    syntax.load_syntax(SettingsTags.NAME + SettingsTags.EXTENTION)
    key = KeyMapRegex()
    key.check_overriding_if_enable()
