import sublime
import sublime_plugin
import json
import re
from os import path
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
        MSG_STRING    = "msg_string"
        BORDER_STRING = "border_string"
        APP_MARK      = "app_mark"

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


def open_file(self, path_to_file, message_if_absent):
    """
    Open file. Show message if file not found

    Parameters
    ----------
    self : class view 
    path_to_file : str
    message_if_absent : str
    """
    if path.isfile(path_to_file):
        self.view.window().open_file(path_to_file)
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
        FULL_PATH_FILE = "(/.*)(/sdl_core/src/.{0,}\\.(cc|h|cpp|hpp)):(\\d{1,})"
        CORRECTED_PATH = "(/[^/ ]*)+/?"
        primaryPath = re.search(FULL_PATH_FILE, self.view.substr(
            self.view.line(self.view.sel()[0])))
        isItPath = re.search(CORRECTED_PATH, self.view.substr(
            self.view.line(self.view.sel()[0])))
        if primaryPath:
            if self.view.settings().get(SettingsTags.SOURCE_PATH):
                file = self.view.settings().get(
                    SettingsTags.SOURCE_PATH) + primaryPath.group(2)
                open_file(self,
                          file, "File '{0}' not found. Maybe path to source files in your settings is incorrect or file really absent".format(file))
            else:
                file = primaryPath.group(1) + primaryPath.group(2)
                open_file(self,
                          file, "File '{0}' not found. You can write path to source files in settings and try again. Or file really absent".format(file))
        elif isItPath:
            sublime.error_message(
                "Expected '/sdl_core/src/' in '{0}' ".format(isItPath.group(0)))


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
