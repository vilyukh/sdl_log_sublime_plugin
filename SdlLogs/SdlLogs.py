import sublime
import sublime_plugin
import json
import re
from os import walk
from os import path
import fnmatch
import shutil
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
    """
    NAME = "SdlLogs"
    EXTENTION = ".sublime-settings"
    SOURCE_PATH = "source_path"


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
        THREAD_ENTER = "thread_enter"
        THREAD_EXIT = "thread_exit"

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
    def run(self, edit):
        sel_text_regex = get_selected_text(self)
        if sel_text_regex is not "":
            trc_regions = self.view.find_all(sel_text_regex)
            left_border = 0
            for i in range(0, len(trc_regions)):
                trc_regions[i] = self.view.full_line(trc_regions[i])
                trc_regions[i] = self.view.substr(trc_regions[i])
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            left_border = 0
            for cur_regions in trc_regions:
                left_border += self.view.insert(edit,
                                                left_border, cur_regions)


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
        FUNC_TREE_BEGIN = ".(cc|h):[0-9]{1,5} (.*)"
        FUNC_TREE_END = "(.*)$"
        sel_text_regex = get_selected_text(self)
        hlText = []
        if sel_text_regex:
            trc_regions = self.view.find_all(
                FUNC_TREE_BEGIN + sel_text_regex + FUNC_TREE_END)
            for i in range(0, len(trc_regions)):
                hlText.append(sublime.Region(trc_regions[i].a+8, 0))
                trc_regions[i] = self.view.substr(trc_regions[i])
                trc_regions[i] = trc_regions[i][trc_regions[i].find(" ")+1:]
                hlText[i].b = hlText[i].a + len(trc_regions[i])
                if trc_regions[i].find(" Exit") is not -1:
                    break
        self.view.add_regions('func_tree', hlText, 'param.func_tree.SDL_Logs')


syntax = LogSyntax()


def plugin_loaded():
    """
    This function will be call when plugin is loaded
    """
    syntax.load_syntax(SettingsTags.NAME + SettingsTags.EXTENTION)
