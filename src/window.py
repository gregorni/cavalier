# window.py
#
# Copyright 2022 Fyodor Sobolev
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.
#
# SPDX-License-Identifier: MIT

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

from .draw import wave, levels
from .cava import Cava
from threading import Thread

settings = Gio.Settings.new('io.github.fsobolev.Cavalier')

class CavalierWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CavalierWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cava_sample = []

        self.build_ui()
        self.connect('close-request', self.on_close_request)

        self.cava = Cava(self)
        self.cava_thread = Thread(target=self.cava.run)
        self.cava_thread.start()

        GObject.timeout_add(1000.0 / 60.0, self.redraw)

    def build_ui(self):
        (width, height) = settings.get_value('size')
        self.set_default_size(width, height)

        self.overlay = Gtk.Overlay.new()
        self.set_content(self.overlay)

        self.drawing_area = Gtk.DrawingArea.new()
        self.drawing_area.set_vexpand(True)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_draw_func(self.draw_func, None, None)
        self.overlay.set_child(self.drawing_area)

        self.header = Adw.HeaderBar.new()
        self.header.add_css_class('flat')
        self.header.set_decoration_layout('')
        self.header.set_title_widget(Gtk.Label.new(''))
        self.overlay.add_overlay(self.header)

        self.menu_button = Gtk.MenuButton.new()
        self.menu_button.set_valign(Gtk.Align.START)
        self.menu_button.set_icon_name('open-menu-symbolic')
        self.header.pack_start(self.menu_button)

        self.menu = Gio.Menu.new()
        self.menu.append(_('Preferences'), 'app.preferences')
        self.menu.append(_('About'), 'app.about')
        self.menu.append(_('Quit'), 'app.quit')
        self.menu_button.set_menu_model(self.menu)

    def draw_func(self, area, cr, width, height, data, n):
        if len(self.cava_sample) > 0:
            levels(self.cava_sample, cr, width, height)

    def redraw(self):
        self.drawing_area.queue_draw()
        return True

    def open_preferences(self, w):
        pass

    def open_about(self, w):
        pass

    def on_close_request(self, w):
        (width, height) = self.get_default_size()
        settings.set_value('size', GLib.Variant.new_tuple( \
            GLib.Variant.new_int32(width), GLib.Variant.new_int32(height)))
        self.cava.stop()

    def quit(self, w):
        self.close()
