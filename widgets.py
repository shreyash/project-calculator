import string

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text.markup import MarkupLabel
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors.touchripple import TouchRippleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.list import (
    CheckboxLeftWidget,
    IconLeftWidget,
    IRightBodyTouch,
    MDList,
    OneLineAvatarIconListItem,
    TwoLineAvatarIconListItem,
)
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDToolbar
from kivymd.utils.fitimage import FitImage

from solve import Basic, Convert
from properties import (
    color,
    config_data,
    current_page,
    days_number,
    hover,
    symbol,
    theme_image,
    write_history,
)


class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, check):
        for item in self.parent.children:
            if item.check_box == check:
                item.check_box.state = "down"
            else:
                item.check_box.state = "normal"

    def __init__(self, **kwargs):
        super(ItemConfirm, self).__init__(**kwargs)
        self.check_box = CheckboxLeftWidget()
        self.add_widget(self.check_box)
        self.check_box.bind(on_release=lambda a: self.set_icon(self.check_box))


class TextField(MDTextField):
    title = StringProperty()

    def on_focus(self, *args):
        super().on_focus(*args)
        if not args[1] and str(type(self.parent.parent.parent).__name__) == "ListItem":
            self.parent.parent.parent.parent.selected.update(
                {
                    self.title: int(args[0].text)
                    if self.title != "base"
                    else args[0].text
                }
            )

    def insert_text(self, substring, from_undo):
        if self.title == "history_length" and substring not in string.digits:
            return
        return super().insert_text(substring, from_undo)

    def on_text_validate(self):
        super().on_text_validate()

    def on_text(self, instance, text):
        super(TextField, self).on_text(instance, text)
        if self.parent == None:
            return
        if str(type(self.parent.parent.parent).__name__) == "ListItem":
            if text == "0":
                self.helper_text = "can't take 0"
                self.helper_text_mode = "on_error"
                self.error = True
                self.focus = True
            elif text == "":
                self.helper_text = "can't be empty"
                self.helper_text_mode = "on_error"
                self.focus = True
                self.error = True
            else:
                self.error = False
        else:
            self.parent.parent.parent.search_func(text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_mode = "custom"

        self.line_color_normal = color(
            f"images/{theme_image[config_data['theme']][2]}.png"
        )
        self.line_color_focus = color(
            f"images/{theme_image[config_data['theme']][0]}.png"
        )
        self.error_color = self.line_color_focus


class Drop(ModalView):
    values = ListProperty()
    default = StringProperty()
    value = StringProperty()
    selection = NumericProperty(-1)
    title = StringProperty()

    def options_select(self, *args):
        self.value = str(args[0].parent.parent.text)

    def search_func(self, text):
        self.searched = []
        for s in self.values:
            if text.lower() in s.lower():
                self.searched.append(s)
        self.old = self.values
        self.values = self.searched
        self.refresh()
        self.values = self.old

    def slide_search(self, *args):
        if self.search_box in self.layout.children:
            self.layout.remove_widget(self.search_box)
        else:
            self.layout.add_widget(self.search_box, index=1)
            Clock.schedule_once(lambda dt: setattr(self.search, "focus", True), 0.1)

    def refresh(self, *args):
        self.options_layout.clear_widgets()
        for options_button_text in self.values:
            options_button = ItemConfirm(text=options_button_text)

            self.options_layout.add_widget(options_button)
            options_button.check_box.bind(
                on_release=lambda options_button=options_button: self.options_select(
                    options_button
                )
            )
        self.temp = list(self.values)
        self.temp.reverse()
        try:
            self.selection = self.temp.index(self.default)
        except:
            self.selection = -1
        if self.values:
            try:
                self.options_layout.children[self.selection].check_box.state = "down"
                if self.value not in self.values:
                    self.value = self.options_layout.children[self.selection].text
            except:
                self.options_layout.children[-1].check_box.state = "down"
                if self.value not in self.values:
                    self.value = self.options_layout.children[-1].text

    def __init__(self, **kwargs):
        super(Drop, self).__init__(**kwargs)
        self.auto_dismiss = False

        self.layout = MyBoxLayout(orientation="vertical")
        self.options_scroll = ScrollView()
        self.options_layout = MDList()
        if not self.default:
            self.default = self.values[0]
        self.refresh()

        self.toolbar = MDToolbar(title=self.title, anchor_title="center", elevation=10)
        self.toolbar.md_bg_color = color(
            f"images/{theme_image[config_data['theme']][2]}.png"
        )
        self.toolbar.specific_text_color = color(
            f"images/{theme_image[config_data['theme']][0]}.png"
        )
        self.search_box = MyBoxLayout(padding=[20, 0], size_hint_y=0.2)
        self.search = TextField(padding_x=10)
        self.search_box.add_widget(self.search)
        self.toolbar.left_action_items = [["magnify", self.slide_search]]
        self.toolbar.right_action_items = [["check", self.dismiss]]
        self.layout.add_widget(self.toolbar)
        self.options_scroll.add_widget(self.options_layout)
        self.layout.add_widget(self.options_scroll)

        self.add_widget(self.layout)


class Icon(MDIconButton):
    theme_text_color = "Custom"
    text_color = color(f"images/{theme_image[config_data['theme']][0]}.png")


class ListItem(TwoLineAvatarIconListItem):
    icon = StringProperty()
    title = StringProperty()
    container = ObjectProperty()
    time = StringProperty()
    width_mult = NumericProperty(1)

    def __init__(self, **kwargs):
        super(ListItem, self).__init__(**kwargs)
        self.theme_text_color = self.secondary_theme_text_color = "Custom"
        self.text_color = color(f"images/{theme_image[config_data['theme']][0]}.png")
        self.secondary_text_color = self.text_color[:3] + [0.7]
        self.container = Container()
        self.ids._right_container.width = self.container.width * self.width_mult
        self.ids._right_container.x = self.container.width * self.width_mult

        if self.icon:
            self.add_widget(IconLeftWidget(icon=self.icon))


class MButton(TouchRippleButtonBehavior, Button):

    background_disabled_normal = StringProperty(
        f"images/{theme_image[config_data['theme']][2]}.png"
    )
    background_down = StringProperty(
        f"images/{theme_image[config_data['theme']][1]}.png"
    )
    background_normal = StringProperty(
        f"images/{theme_image[config_data['theme']][2]}.png"
    )
    bold = BooleanProperty(False)
    color = ColorProperty(color(f"images/{theme_image[config_data['theme']][0]}.png"))
    hover = BooleanProperty(True)
    hover_image = StringProperty(f"images/{theme_image[config_data['theme']][1]}.png")
    icon = StringProperty(None)
    icon_opacity = NumericProperty(1)
    icon_padding = NumericProperty(10)
    icon_rotation = NumericProperty(0)
    icon_size = ObjectProperty((30, 30))
    modal_button = BooleanProperty(False)
    old_font_size = NumericProperty(9)
    ripple = BooleanProperty(True)
    ripple_color = ListProperty()
    ripple_fade_from_alpha = NumericProperty(0.8)
    ripple_fade_to_alpha = NumericProperty(0.8)
    ripple_rad_default = NumericProperty(5)
    state_enable = BooleanProperty(True)
    toggle_state = BooleanProperty(False)

    def on_disabled(self, instance, value):
        pass

    def on_press(self):
        if self.state_enable:
            if self.toggle_state:
                if self.state == "normal":
                    self.state = "down"
                else:
                    self.state = "normal"
            else:
                self.state = "down"

    def on_release(self):
        if self.state_enable and not self.toggle_state:
            self.state = "normal"
        if self.state == "down":
            self.color = self.hover_color

    def on_touch_down(self, touch):
        if self.disabled or not self.ripple:
            return False
        collide_point = self.collide_point(touch.x, touch.y)
        if collide_point:
            touch.grab(self)
            self.ripple_show(touch)

            self.dispatch("on_press")
            return True
        return False

    def on_touch_up(self, touch):
        if self.disabled:
            return False
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()

            def defer_release(dt):

                self.dispatch("on_release")

            Clock.schedule_once(defer_release, self.ripple_duration_out)
            return True
        return False

    def mouse_pos(self, window, pos, **kwargs):
        if self.state == "down":
            return
        if not hover[0] and not self.modal_button or self.disabled or not self.hover:
            self.background_normal = self.old_image
            self.color = self.color_
            return

        if self.collide_point(*pos):
            self.color = self.hover_color
            self.background_normal = self.hover_image

        else:
            self.color = self.color_
            self.background_normal = self.old_image

    def on_size(self, *args):
        change = (self.size[0] * 0.5 + self.size[1] * 0.5) * self.old_font_size * 0.01
        max_size = 20
        self.font_size = min(change, max_size)

    def __init__(self, **kwargs):
        super(MButton, self).__init__(**kwargs)
        self.old_font_size = max(9, self.font_size)
        self.old_image = self.background_normal
        self.color_ = self.color
        self.hover_color = (
            1 - self.color[0],
            1 - self.color[1],
            1 - self.color[2],
            self.color[3],
        )
        self.ripple_color = color(f"images/{theme_image[config_data['theme']][3]}.png")
        if not self.hover:
            self.hover_image = self.background_normal

        if self.hover_image:
            Window.bind(mouse_pos=self.mouse_pos)


class Text(TextInput):
    foreground_color = ListProperty(
        color(f"images/{theme_image[config_data['theme']][0]}.png")
    )
    background_active = StringProperty(
        f"images/{theme_image[config_data['theme']][2]}.png"
    )
    cursor_color = ListProperty(
        color(f"images/{theme_image[config_data['theme']][0]}.png")
    )
    cursor_width = dp(5)
    from_unit = StringProperty()
    minimum_width = NumericProperty(1)
    to_unit = StringProperty()
    write_tab = False
    quantity = StringProperty()
    solved = False
    last_press = StringProperty()

    def on_focus(self, instance, value):
        def real(dt):
            if self.text == "":
                self.insert_text("0")

        Clock.schedule_once(real, 3)

    def on_cursor(self, instance, newPos):
        self.width = max(self.minimum_width, self.parent.width)

        if not (isinstance(self.parent, ScrollView) and self.multiline):
            return super(Text, self).on_cursor(instance, newPos)
        if newPos[0] == 0:
            self.parent.scroll_x = 0
        else:
            over_width = self.width - self.parent.width
            if over_width <= 0.0:
                return super(Text, self).on_cursor(instance, newPos)
            view_start = over_width * self.parent.scroll_x
            view_end = view_start + self.parent.width
            offset = self.cursor_offset()
            desired_view_start = offset - 5
            desired_view_end = (
                offset + self.padding[0] + self.padding[2] + self.cursor_width + 5
            )
            if desired_view_start < view_start:
                self.parent.scroll_x = max(0, desired_view_start / over_width)
            elif desired_view_end > view_end:
                self.parent.scroll_x = min(
                    1, (desired_view_end - self.parent.width) / over_width
                )
        return super(Text, self).on_cursor(instance, newPos)

    def replace(self, exp):
        exp = exp.replace("sqrt", "math.sqrt")
        exp = exp.replace("^", "**")
        exp = exp.replace("x", "*")
        exp = exp.replace("÷", "/")
        exp = exp.replace("ceil", "math.ceil")
        exp = exp.replace("floor", "math.floor")
        exp = exp.replace("\u03c0", "math.pi")
        exp = exp.replace("e","math.e")
        return exp

    def fac_solve(self, exp):
        for x in ("+", "-", "/", "*", "**"):
            exp = exp.replace(x, f" {x} ")
        exp = exp.split()

        for x_index, x in enumerate(exp):
            if "!" in x:
                if x[-1] == "!":
                    exp[x_index] = "math.factorial({})".format(x.replace("!", ""))
                else:
                    return "symbol error"

        if "factorial()" in exp:
            return "Can't calculate factorial of nothing!"
        else:
            return str("".join(exp))

    def insert_text(self, substring, from_undo=False):
        self.page = self.parent.parent.parent

        if substring == "AC":
            self.text = ""
            return
        if substring == "Del":
            if self.last_press in "\r\n=":
                self.insert_text("AC")
            else:
                self.do_backspace()
            return
        
            
        if substring == "*":
            substring = "x"

        if substring == "**":
            substring = "^"

        if substring == "/":
            substring = "÷"

        if substring == "a\u00b2":
            substring = "^2"

        if substring == "ceil":
            if self.selection_text:
                self.text = self.text.replace(self.selection_text,f"ceil({self.selection_text})")
            else:
                self.text = f"ceil({self.text})"
            return
        if substring == "|a|":
            if self.selection_text:
                self.text = self.text.replace(self.selection_text,f"abs({self.selection_text})")
            else:
                self.text = f"abs({self.text})"
            return
        if substring == "floor":
            if self.selection_text:
                self.text = self.text.replace(self.selection_text,f"floor({self.selection_text})")
            else:
                self.text = f"floor({self.text})"
            return
        if substring == "\u221aa":
            if self.selection_text:
                self.text = self.text.replace(self.selection_text,f"sqrt({self.selection_text})")
            else:
                self.text = f"sqrt({self.text})"
            return

        if substring == "a!":
            substring = "!"

        if substring == str(config_data['base'])+'\u00aa':
            substring = str(config_data['base'])+'^'

        if self.last_press in "+-÷x^%\u00b1":
            if self.last_press == substring:
                return
            else:
                if self.text and substring in "+-÷x^%":
                    self.do_backspace()

        if substring in "÷x^" and (self.text == "0" or not self.text):
            return

        if (
            (
                current_page[0] == "standard"
                and substring not in string.digits + "%()+-x÷^.!=\r\n"
                and substring != "^2"
            )
            or (
                current_page[0] == "scientific"
                and substring not in string.digits + "%()e+-x÷^.!sincotae=\r\n"
                and substring != "^2"
                and substring not in ['sin','cos','tan','cosec','cot','sec','log']
                and substring not in ['sin\u00af\u00b9','cos\u00af\u00b9','tan\u00af\u00b9','cosec\u00af\u00b9','cot\u00af\u00b9','sec\u00af\u00b9']
                and substring != str(config_data['base']+'^')
                and substring != '\u03c0'
            )
            or (
                current_page[0] == "convert"
                and substring not in string.digits + ".=\r\n"
            )
            or (current_page[0] == "days" and substring not in string.digits + "=\r\n")
        ):
            return
        self.last_press = substring
        if substring in ["\r", "\n", "="]:
            if self.text[-1] in "+-÷x^(%":
                self.page.preview.text = "Complete the equation first!"
                return
            self.last_press = substring
            for opr in "+-÷x^()!%":
                if self.text.count(opr):
                    break
            else:
                if current_page[0] not in ["convert", "days"]:
                    return
            self.page.old_text = self.text
            self.page.preview.text = "[ref=self.old_text]" + self.text + "[/ref]"

            if current_page[0] == "standard":
                substring = self.text
                substring = self.replace(substring)
                if "!" in self.text:
                    substring = self.fac_solve(self.text)
                try:
                    substring = Basic(exp=substring).solution
                except:
                    self.page.preview.text = (
                        "There's some error, could you check please?"
                    )
                    return
            elif current_page[0] == "scientific":
                substring = self.text
                substring = self.replace(substring)
                if "!" in substring:
                    substring = self.fac_solve(substring)

                rad = 1 if self.page.layout.buttons[0][2].state == "down" else 0
                for r in ["sin", "tan", "cos", "cot", "cosec", "sec"]:
                    substring = substring.replace(r, f"Basic(rad={rad}).{r}")
                for r in ["sin\u00af\u00b9", "tan\u00af\u00b9", "cos\u00af\u00b9", "cot\u00af\u00b9", "cosec\u00af\u00b9", "sec\u00af\u00b9"]:
                    r1 = r.replace("\u00af\u00b9", "")
                    substring = substring.replace(r, f"a{r1}")
                substring = substring.replace(
                    "log", f"Basic(base={config_data['base']}).log"
                )
                from math import factorial

                try:
                    substring = Basic(exp=substring).solution
                except:
                    self.page.preview.text = "Something went wrong!"
                    return
            elif current_page[0] == "convert":
                try:
                    substring = (
                        str(
                            eval("Convert." + self.quantity)(
                                self.text.split()[0], self.from_unit, self.to_unit
                            )
                        )
                        + " "
                        + self.to_unit
                    )
                    self.page.preview.text = (
                        "[ref=self.old_text]"
                        + self.text
                        + " "
                        + self.from_unit
                        + "[/ref]"
                    )
                except:
                    self.page.preview.text = "There's some error!"
                    return
            elif current_page[0] == "days":
                try:
                    substring = days_number(
                        self.page.layout.buttons[1][0].text,
                        self.page.layout.buttons[1][2].text,
                    )
                    if self.page.layout.buttons[2][-1].state == "down":
                        substring += 1
                    if self.page.layout.buttons[3][-1].state == "down":
                        substring -= 1
                    substring = str(substring)
                    self.page.preview.text = f"{self.page.layout.buttons[1][0].text} to {self.page.layout.buttons[1][2].text}"
                except:
                    self.page.preview.text = "Oops! Couldn't find that!"
                    return
            self.solved = True
            write_history(
                self.page.preview.text
                if current_page[0] == "days"
                else MarkupLabel(self.page.preview.text).markup[1],
                substring,
                current_page[0],
            )
            self.text = ""

        if self.text == "0" and substring != ".":
            self.do_backspace()
        for sub_ in substring:
            return super(Text, self).insert_text(substring, from_undo=from_undo)

    def on_text(self, instance, newText):

        width_calc = 0
        for line_label in self._lines_labels:
            width_calc = max(width_calc, line_label.width + 90)
        self.minimum_width = width_calc

    def keyboard_on_key_up(self, window, keycode):

        if keycode[1] == "right" or keycode[1] == "left":
            self.calc_scroll(keycode[1], True)

        key, key_str = keycode
        k = self.interesting_keys.get(key)
        if k:
            key = (None, None, k, 1)
            self._key_up(key)

    def calc_scroll(self, direction, key=None):

        if not key:
            self.do_cursor_movement("cursor_" + direction)

        if direction == "left":
            limit = ">0"
            sensitivity = "-"
        else:
            limit = "<1"
            sensitivity = "+"

        if eval("self.parent.scroll_x" + limit):
            self.parent.scroll_x += eval(sensitivity + "0.07")
        else:
            self.parent.scroll_x = limit[1:]

        if self.cursor_col == len(self.text):
            self.parent.scroll_x = 1

    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.background_disabled_normal = self.background_active
        self.background_normal = self.background_active


class MyBoxLayout(BoxLayout):
    color = ListProperty(color(f"images/{theme_image[config_data['theme']][2]}.png"))

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color)
            Rectangle(pos=self.pos, size=self.size)


class Container(IRightBodyTouch, BoxLayout):
    adaptive_width = True


class ClipButtons(MyBoxLayout):
    copy_button = ObjectProperty()
    cut_button = ObjectProperty()
    paste_button = ObjectProperty()

    def clip_action(self, *args, **kwargs):
        input = self.parent.parent.parent.pages.current_screen.children[0].entry
        data = input.selection_text if input.selection_text else input.text

        if args[0].icon == "content-copy":
            input.copy(data)
        elif args[0].icon == "content-cut":
            input._cut(data)
            if data == input.text:
                input.text = ""
        elif args[0].icon == "content-paste":
            input.paste()
        input.delete_selection()

    def __init__(self, *args, **kwargs):

        super(ClipButtons, self).__init__(**kwargs)

        self.copy_button = Icon(icon="content-copy")
        self.cut_button = Icon(icon="content-cut")
        self.paste_button = Icon(icon="content-paste")

        for widget in (self.copy_button, self.cut_button, self.paste_button):
            widget.bind(on_release=self.clip_action)
            self.add_widget(widget)


class MLabel(Label):
    color = ListProperty(color(f"images/{theme_image[config_data['theme']][0]}.png"))
    halign = StringProperty("center")
    valign = StringProperty("center")
    line_height = NumericProperty(1.5)

    def __init__(self, *args, **kwargs):
        super(MLabel, self).__init__(**kwargs)

        self.bind(size=self.setter("text_size"))


class Date(MDDatePicker):

    button = ObjectProperty()

    def on_dismiss(self, *args):
        if args:
            date = args[0].strftime(config_data["format"])
            self.button.text = date
        self.button.parent.parent.parent.parent.parent.parent.parent.parent.options_close()

    def __init__(self, **kwargs):
        super(Date, self).__init__(**kwargs, callback=self.on_dismiss)


class SwipeHover(RelativeLayout):
    radius = NumericProperty()
    source = StringProperty()
    title = StringProperty()

    def __init__(self, **kwargs):
        super(SwipeHover, self).__init__(**kwargs)
        self.image_container = MDCard(
            radius=[
                self.radius,
            ]
        )
        self.image = GridLayout(cols=2, rows=2)

        for index, text in enumerate(["pressed", "hover", "text", "normal"]):
            new = FitImage(
                source=f"images/{text}{self.source}.png", radius=[0, 0, 0, 0]
            )
            new.radius[index] = self.radius
            self.image.add_widget(new)
        self.image.children[0], self.image.children[1] = (
            self.image.children[1],
            self.image.children[0],
        )
        self.image_container.add_widget(self.image)
        self.image1 = FitImage(
            source=f"images/{theme_image[config_data['theme']][1]}.png",
            radius=[0],
            size_hint=(0, 0),
            pos_hint={"center_x": 0.5, "center_y": -0.5},
        )
        self.image2 = FitImage(
            source=f"images/{theme_image[config_data['theme']][3]}.png",
            radius=[0],
            size_hint=(0, 0),
            pos_hint={"center_x": 0.5, "center_y": -0.5},
        )
        self.text = MLabel(
            text=self.title,
            font_size=0,
            padding=[0, dp(40)],
            color=color(f"images/{theme_image[config_data['theme']][2]}.png")[:3] + [0],
        )

        self.select = MDCheckbox(
            size_hint=(0, 0),
            pos_hint={"center_x": 0.5, "center_y": -0.5},
            group="group",
        )
        self.select.update_color()
        self.select.update_primary_color(self, self.text.color[:3] + [1])
        self.select.bind(
            on_press=lambda a: self.parent.parent.parent.parent.parent.parent.theme(a)
        )
        self.add_widget(self.image_container)
        self.add_widget(self.text)
        self.add_widget(self.select)


class Swiper(MDSwiperItem, HoverBehavior):
    radius = 20
    source = StringProperty()
    canvas_opacity = NumericProperty(0)
    title = StringProperty()
    hover = BooleanProperty(False)

    def on_leave(self, *args):
        Animation(
            radius=[500],
            pos_hint={"center_y": -0.5},
            size_hint=(0, 0),
            duration=0.6,
            t="in_out_cubic",
        ).start(self.layout.image1)
        Animation(
            radius=[500],
            pos_hint={"center_y": -0.5},
            size_hint=(0, 0),
            duration=0.8,
            t="in_out_cubic",
        ).start(self.layout.image2)
        Animation(
            font_size=dp(0),
            color=self.layout.text.color[:3] + [0],
            padding=[0, dp(40)],
            duration=0.5,
            t="in_out_sine",
        ).start(self.layout.text)
        Animation(
            pos_hint={"center_y": -0.5},
            size_hint=(0, 0),
            duration=0.8,
            t="in_out_cubic",
        ).start(self.layout.select)

    def on_enter(self):
        if not self.hover:
            self.on_leave()
            return
        Animation(
            radius=[self.radius],
            pos_hint={"center_y": 0.5},
            size_hint=(1, 1),
            duration=0.8,
            t="in_out_cubic",
        ).start(self.layout.image1)
        Animation(
            radius=[self.radius],
            pos_hint={"center_y": 0.5},
            size_hint=(1, 1),
            duration=0.6,
            t="in_out_cubic",
        ).start(self.layout.image2)
        Animation(
            font_size=dp(30),
            color=self.layout.text.color[:3] + [1],
            padding=[0, 0],
            duration=0.8,
            t="in_out_sine",
        ).start(self.layout.text)
        Animation(
            pos_hint={"center_y": 0.3},
            size_hint=(0.2, 0.3),
            duration=0.8,
            t="in_out_cubic",
        ).start(self.layout.select)

    def __init__(self, **kwargs):
        super(Swiper, self).__init__(**kwargs)
        self.layout = SwipeHover(
            source=self.source, radius=self.radius, title=self.title
        )
        self.layout.add_widget(self.layout.image1, index=2)
        self.layout.add_widget(self.layout.image2, index=3)
        self.add_widget(self.layout)