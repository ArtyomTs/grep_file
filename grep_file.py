import sublime, sublime_plugin
import os, re

def is_legal_path_char(c):
    # XXX make this platform-specific?
    return c not in " \n\"|*<>{}[](),\':"

def move_while_path_character(view, start, is_at_boundary, increment=1):
    while True:
        if not is_legal_path_char(view.substr(start)):
            break
        start = start + increment
        if is_at_boundary(start):
            break
    return start

def is_controller(dir):
    regex = re.compile('(controllers)')
    match = regex.findall(dir)
    return match

def with_path(fname):
    regex = re.compile('(\S*/\S+)')
    match = regex.findall(fname)
    return match

class GrepFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        prefix = ""

        caret_pos = self.view.sel()[0].begin()
        current_line = self.view.line(caret_pos)
        line_text = self.view.substr(sublime.Region(current_line.begin(), current_line.end()))

        dir = self.get_working_dir()

        if is_controller(dir):
            prefix = self.prefix_for_controller(line_text)
        else:
            True

        sel = self.view.sel()[0]
        if not sel.empty():
            file_name = self.view.substr(sel)
        else:
            

            left = move_while_path_character(
                                            self.view,
                                            caret_pos,
                                            lambda x: x < current_line.begin(),
                                            increment=-1)
            right = move_while_path_character(
                                            self.view,
                                            caret_pos,
                                            lambda x: x > current_line.end(),
                                            increment=1)
            file_name = self.view.substr(sublime.Region(left + 1, right))
            if with_path(file_name):
                prefix = ""
            else:
                True
            self.view.window().run_command("show_overlay", {"overlay": "goto", "show_files": True, "text": prefix + file_name} )

        # file_name = os.path.join(os.path.dirname(self.view.file_name()),
        #                             file_name)
        # if os.path.exists(file_name):
        #     self.view.window().open_file(file_name)
    def get_working_dir(self):
        file_name = self._active_file_name()
        if file_name:
          return os.path.dirname(file_name)
        else:
          return self.window.folders()[0]

    def _active_file_name(self):
        view = self.view;
        if view and view.file_name() and len(view.file_name()) > 0:
          return view.file_name()

    def prefix_for_controller(self, line):
        regex = re.compile('(def|render)')
        match = regex.findall(line)
        regex = re.compile('\S+\/(\S+)_controller')
        full_name = self._active_file_name()
        fname = regex.findall(full_name)
        if fname:
            return fname[0] + '/'
        else:
            return ""
