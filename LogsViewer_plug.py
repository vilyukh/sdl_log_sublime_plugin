import sublime
import sublime_plugin
import json

#Regulars for columns:
dateRegex       = "\\[\\s?[0-9]{1,2} \\s?[A-Z][a-z]{2} [0-9]{4} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2},[0-9]{0,3}]"
junkRegex       = " /(.*)/sdl_core/src/" 
componentRegex  = "\\[[A-Z][a-zA-z]{3,26}] "
threadEnter     = ".(cc|h):[0-9]{1,5} (.*): Enter"
threadExit      = " Exit"
threadRegex     = "\\[0x[a-zA-Z0-9]{12}]"
pathRegex       = "sdl_core/src/(.*).(cc|h):[0-9]{1,5}" 

#flags for commands
actThreadFlag    = False
actDateFlag      = False
actPathFlag      = False
actComponentFlag = False



def getSelectedText(self):
	#array of selection regions
	selText = self.view.sel()
	#selected string
	selText = self.view.substr(selText[0])
	return selText


#Hide date of all traces from log
class HideDateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global actDateFlag
		trcRegions = self.view.find_all(dateRegex)

		if actDateFlag is False:
			self.view.fold(trcRegions)
			actDateFlag = True
		else:
			self.view.unfold(trcRegions)
			actDateFlag = False


class FunctionCallCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		posFatal = 0
		enterRegex = "initial fake value"

		while enterRegex is not "":

			enterRegion = self.view.find(threadEnter, posFatal)
			enterRegex = self.view.substr(enterRegion)
			enterRegex = enterRegex[enterRegex.find(" ")+1:]
			enterRegex = enterRegex[:enterRegex.find(" ")]

			print (enterRegex)

			if enterRegex is not "":
				exitRegion = self.view.find(enterRegex+threadExit, posFatal)
				print (self.view.substr(exitRegion))

				if exitRegion.size() is not 0:
					posFatal = enterRegion.b
				else:
					self.view.show(enterRegion)
					posFatal = enterRegion.b
					break




class HideThreadAdressCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global actThreadFlag
		trcRegions = self.view.find_all(threadRegex)

		if actThreadFlag is False:
			self.view.fold(trcRegions)
			actThreadFlag = True
		else:
			self.view.unfold(trcRegions)
			actThreadFlag = False


class HideComponentCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global actComponentFlag
		trcRegions = self.view.find_all(componentRegex)

		if actComponentFlag is False:
			self.view.fold(trcRegions)
			actComponentFlag = True
		else:
			self.view.unfold(trcRegions)
			actComponentFlag = False


class HideExtraPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global actPathFlag
		trcRegions = self.view.find_all(junkRegex)

		if actPathFlag is False:
			self.view.fold(trcRegions)
			actPathFlag = True
		else:
			self.view.unfold(trcRegions)
			actPathFlag = False


class FilterByValueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		selTextRegex = getSelectedText(self)
		if selTextRegex is not "":
			trcRegions = self.view.find_all(selTextRegex)
			cutRegion = sublime.Region(0, 0)
			leftBorder = 0

			for i in range (0, len(trcRegions)):
				trcRegions[i] = self.view.full_line(trcRegions[i])
				trcRegions[i] = self.view.substr(trcRegions[i])

			self.view.erase(edit, sublime.Region(0, self.view.size()))
			leftBorder = 0

			for i in range (0, len(trcRegions)):
				leftBorder+= self.view.insert(edit, leftBorder, trcRegions[i])


