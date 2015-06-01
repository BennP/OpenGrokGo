import sublime, sublime_plugin
import webbrowser
import re
import sys

class OpenGrokGoCommand(sublime_plugin.TextCommand):
    def run(self, edit, code_direction):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line) + '\n'
                o_settings = OpenGrokGo_Settings()
                o_line = OpenGrokGo_Line()
                new_line = o_line.extract_line(line_contents, o_settings.get_modules(),code_direction)
                if new_line == "":
                    sublime.status_message(('Not a line that can be used to jump to OpenGrok') )
                    return
                else:
                    url_grok = o_settings.get_url() + '/xref/' + o_settings.get_version() + '/' + new_line
                    self.OG_openUrl(url_grok)
                    return
            else:
                return

    def OG_openUrl(self, url_in):
        # open a public URL, in this case, the webbrowser docs
        new = 2; # open in a new tab, if possible

        webbrowser.open(url_in,new=new);

class OpenGrokVersionCommand(sublime_plugin.WindowCommand):
    version_list = []
    def run(self):
        # open an input box to choose a version
        self.v_settings = OpenGrokGo_Settings()
        self.version_list = self.v_settings.get_versions()
        self.window.show_quick_panel(self.version_list, self.on_done)
        return

    def on_done(self, picked):
        # now try to write this text to the panel
        if picked == -1:
            return
        version = self.version_list[picked]
        self.v_settings.set_version(version)
        sublime.status_message(('Version %s successfully set for OpenGrok') %
            version)


class OpenGrokGo_Settings(sublime_plugin.ApplicationCommand):
    'Common base class for settings to the OpenGrokGo plugin'
    tot_row = 0

    def __init__(self):
        pass
    def get_version(self):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        current = s.get("astro_version", 'X.X')
        return current

    def set_version(self,new_version):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        s.set("astro_version", new_version)
        sublime.save_settings("Open Grok Go.sublime-settings")

    def get_versions(self):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        current_list = s.get("astro_versions")
        return current_list

    def set_versions(self,new_version_list):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        s.set("astro_versions", new_version_list)
        sublime.save_settings("Open Grok Go.sublime-settings")

    def get_url(self):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        current = s.get("opengrok_url", 'http://opengrok.rd.consafe1.org/opengrok')
        return current

    def set_url(self,new_url):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        s.set("opengrok_url", new_url)
        sublime.save_settings("Open Grok Go.sublime-settings")

    def get_modules(self):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        current = s.get("astro_modules")
        return current

    def set_modules(self,new_module_list):
        s = sublime.load_settings("Open Grok Go.sublime-settings")
        s.set("astro_modules", new_url)
        sublime.save_settings("Open Grok Go.sublime-settings")

class OpenGrokGo_Line:
    'Common base class for extracting a usable string to send to OpenGrok'

    def __init__(self):
        pass

    def extract_line(self, line, modules, code_direction):
        'Files containg this pattern .c:34314'
        matchObj = re.search( r'\.{1}[c]{1}[:][0-9]+,', line, re.M|re.I)
        if matchObj:
            if line.find('APPL-OK   : :      :') != -1:
                offset = line.find('OK   : :      :');
                if offset == -1:
                    return ""
                else:
                    num = line[(offset + 16):(offset + 20)].split(':',2)
                    indent_number = int (num[0])
                    indent_str = '                                                              '
                    offset_tail = line.find('./');
                    if offset == -1:
                        return ""
                    file_parts = line[(offset_tail + 1 ):].split(',',4)
                    new_line = ' '
                    if code_direction == "Caller":
                        file_path = file_parts[0]
                    else:
                        # This is the Called part to use later file_parts[2]
                        file_path = file_parts[2]
                    for module in modules:
                        offset_module = file_path.find(module);
                        if offset_module != -1:
                            return file_path[offset_module:].replace(':', '#')
                    return ""

            else:
                return 0

        else:
            return ""