from itertools import chain

from . import resource
from .colors import *
from .view import current as current_view


class Theme(object):
    """A theme is a hierarchical set of view style attributes.

    Each view may have a set of attributes that control its
    visual style when rendered.  These style attributes are stored
    in a Theme.

    Style attributes are hierarchical in that a view class
    may override the style attribute of a parent view class.
    Also, a view class need not override all style attributes
    of a parent view class.

    For instance, let's say we define the default view background
    color to be gray and the border color to be black.

        a_theme.set(class_name='View',
                    state='normal',
                    key='background_color',
                    value=(128, 128, 128))

        a_theme.set(class_name='View',
                    state='normal',
                    key='border_color',
                    value=(0, 0, 0))

    Let's assume this is the only style information defined for View.
    Now, let's override the background color for a Button, add a
    style attribute for the text color, and leave the border color.

        a_theme.set(class_name='Button',
                    state='normal',
                    key='background_color',
                    value=(64, 64, 64))

        a_theme.set(class_name='Button',
                    state='normal',
                    key='text_color',
                    value=(128, 0, 0))

    When a view is stylized (see View.stylize), style attributes and
    values are queried in the current Theme and set on the view instance.

        b = Button()
        b.state = 'normal'
        b.stylize()

    The style attributes set on 'b' would be:

        background_color: (64, 64, 64)  from Button
        border_color: (0, 0, 0)         from View
        text_color: (128, 0, 0)         from Button

    Note that the 'key' is really a 'key path' which would allow you
    to style views contained in other views. For instance, an AlertView
    has a `title_label` which is a Label.  You may wish to style
    AlertView titles differently than other labels, and you can.  See
    the `light_theme` entry for `title_label`. Also see the `kvc` module
    for a simple form of Apple's Key-Value Coding for Python.

    """

    def __init__(self):
        self._styles = {}

    def set(self, class_name, state, key, value):
        """Set a single style value for a view class and state.

        class_name

            The name of the class to be styled; do not
            include the package name; e.g. 'Button'.

        state

            The name of the state to be stylized. One of the
            following: 'normal', 'focused', 'selected', 'disabled'
            is common.

        key

            The style attribute name; e.g. 'background_color'.

        value

            The value of the style attribute; colors are either
            a 3-tuple for RGB, a 4-tuple for RGBA, or a pair
            thereof for a linear gradient.

        """
        self._styles.setdefault(class_name, {}).setdefault(state, {})
        self._styles[class_name][state][key] = value

    def set_for_class(self, class_name, params):
        """
            Set a multi style value for a view class.

        :param class_name: The name of the class to be styled; do not
            include the package name; e.g. 'Button'
        :param params: list of tuples, ('focused', 'background_color', black)
        :return: None
        """
        self._styles.setdefault(class_name, {})
        for state, key, value in sorted(params, key=lambda x: x[0]):
            self._styles[class_name].setdefault(state, {})
            self._styles[class_name][state][key] = value

    def set_for_theme(self, params):
        """
        Set a style for theme
        :param params: list of tuples, [
            (
                'Button',
                [
                    ('focused', 'background_color', black),
                    ...,
                ]
            ),
            ...,
        ]
        :return: None
        """
        for class_name, args in params:
            self.set_for_class(class_name, args)

    def get_dict_for_class(self, class_name, state=None, base_name='View'):
        """The style dict for a given class and state.

        This collects the style attributes from parent classes
        and the class of the given object and gives precedence
        to values thereof to the children.

        The state attribute of the view instance is taken as
        the current state if state is None.

        If the state is not 'normal' then the style definitions
        for the 'normal' state are mixed-in from the given state
        style definitions, giving precedence to the non-'normal'
        style definitions.

        """
        classes = []
        klass = class_name

        while True:
            classes.append(klass)
            if klass.__name__ == base_name:
                break
            klass = klass.__bases__[0]

        if state is None:
            state = 'normal'

        style = {}

        for klass in classes:
            class_name = klass.__name__

            try:
                state_styles = self._styles[class_name][state]
            except KeyError:
                state_styles = {}

            if state != 'normal':
                try:
                    normal_styles = self._styles[class_name]['normal']
                except KeyError:
                    normal_styles = {}

                state_styles = dict(chain(normal_styles.items(),
                                          state_styles.items()))

            style = dict(chain(state_styles.items(),
                               style.items()))

        return style

    def get_dict(self, obj, state=None, base_name='View'):
        """The style dict for a view instance.

        """
        return self.get_dict_for_class(class_name=obj.__class__,
                                       state=obj.state,
                                       base_name=base_name)

    def get_value(self, class_name, attr, default_value=None,
                  state='normal', base_name='View'):
        """Get a single style attribute value for the given class.

        """
        styles = self.get_dict_for_class(class_name, state, base_name)
        try:
            return styles[attr]
        except KeyError:
            return default_value


current = None
light_theme = Theme()
dark_theme = Theme()


def use_theme(theme):
    """Make the given theme current.

    There are two included themes: light_theme, dark_theme.
    """
    global current
    current = theme
    if current_view is not None:
        current_view.stylize()


def init_light_theme():
    color1 = (227, 227, 159)    # a light yellow
    color2 = (173, 222, 78)     # a light green
    color3 = (77, 148, 83)      # a dark green
    color4 = white_color
    color5 = near_white_color
    color6 = light_gray_color
    color7 = gray_color
    color8 = dark_gray_color
    color9 = black_color
    theme = Theme()
    theme.label_height = 16 + 6 * 2  # font size + padding above/below
    theme.button_height = 16 + 6 * 2  # font size + padding above/below
    theme.shadow_size = 140
    theme.set_for_theme(
        [
            (
                'View',
                [
                    ('normal', 'background_color', (color4, color5)),
                    ('focused', 'background_color', (color1, color2)),
                    ('selected', 'background_color', (color1, color2)),
                    ('normal', 'border_color', color6),
                    ('normal', 'border_widths', 0),
                    ('normal', 'margin', (6, 6)),
                    ('normal', 'padding', (0, 0)),
                    ('normal', 'shadowed', False),
                ]
            ),
            (
                'Scene',
                [
                    ('normal', 'background_color', (color5, color4))
                ]
            ),
            (
                'Label',
                [
                    ('normal', 'text_color', color8),
                    ('selected', 'text_color', color3),
                    ('normal', 'text_shadow_color', color4),
                    ('normal', 'text_shadow_offset', (0, 1)),
                    ('normal', 'padding', (6, 6)),
                    ('normal', 'border_widths', None),
                    ('normal', 'font', resource.get_font(16)),
                ]
            ),
            (
                'Button',
                [
                    ('normal', 'background_color', (color4, color6)),
                    ('focused', 'background_color', color1),
                    ('normal', 'text_color', color8),
                    ('normal', 'font', resource.get_font(16, use_bold=True)),
                    ('normal', 'border_widths', 1),
                    ('normal', 'border_color', color6),
                ]
            ),
            (
                'ImageButton',
                [
                    ('normal', 'background_color', (color4, color6)),
                    ('focused', 'background_color', color1),
                    ('normal', 'border_color', color6),
                    ('normal', 'border_widths', 1),
                    ('normal', 'padding', (6, 6)),
                ]
            ),
            (
                'ScrollbarThumbView',
                [
                    ('normal', 'background_color', (color4, color6)),
                    ('focused', 'background_color', (color1, color2)),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'ScrollbarView',
                [
                    ('normal', 'background_color', color5),
                    ('normal', 'border_widths', (1, 1, 0, 0)),
                ]
            ),
            (
                'ScrollView',
                [
                    ('normal', 'hole_color', whites_twin_color),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'SliderTrackView',
                [
                    ('normal', 'background_color', (color5, color4)),
                    ('normal', 'value_color', (color1, color2)),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'SliderView',
                [
                    ('normal', 'background_color', clear_color),
                    ('normal', 'border_widths', None),
                ]
            ),
            (
                'ImageView',
                [
                    ('normal', 'background_color', None),
                    ('normal', 'padding', (0, 0)),
                ]
            ),
            (
                'Checkbox',
                [
                    ('normal', 'background_color', clear_color),
                    ('normal', 'padding', (0, 0)),
                    ('focused', 'check_label.background_color', (color1, color2)),
                    ('normal', 'check_label.border_widths', 1),
                    ('normal', 'label.background_color', clear_color),
                ]
            ),
            (
                'SpinnerView',
                [
                    ('normal', 'border_widths', None)
                ]
            ),
            (
                'DialogView',
                [
                    ('normal', 'background_color', (color4, color6)),
                    ('normal', 'shadowed', True),
                ]
            ),
            (
                'AlertView',
                [
                    ('normal', 'title_label.background_color', color7),
                    ('normal', 'title_label.text_color', color4),
                    ('normal', 'title_label.text_shadow_offset', None),
                    ('normal', 'message_label.background_color', clear_color),
                    ('normal', 'font', resource.get_font(16)),
                    ('normal', 'padding', (6, 6)),
                ]
            ),
            (
                'NotificationView',
                [
                    ('normal', 'background_color', (color1, color2)),
                    ('normal', 'border_color', color3),
                    ('normal', 'border_widths', (0, 2, 2, 2)),
                    ('normal', 'padding', (0, 0)),
                    ('normal', 'message_label.background_color', clear_color),
                ]
            ),
            (
                'SelectView',
                [
                    ('normal', 'disclosure_triangle_color', color8),
                    ('normal', 'border_widths', 1),
                    ('normal', 'top_label.focusable', False),
                ]
            ),
            (
                'TextField',
                [
                    ('focused', 'label.background_color', (color1, color2)),
                    ('normal', 'placeholder_text_color', color6),
                    ('normal', 'border_widths', 1),
                    ('normal', 'text_color', color9),
                    ('disabled', 'text_color', color6),
                    ('normal', 'blink_cursor', True),
                    ('normal', 'cursor_blink_duration', 450),
                ]
            ),
            (
                'GridView',
                [
                    ('normal', 'background_color', color4),
                    ('normal', 'line_color', color6),
                ]
            )
        ]
    )
    return theme


def init_dark_theme():
    # TODO
    pass


def init_dracula_theme():
    theme = Theme()
    theme.label_height = 16 + 6 * 2  # font size + padding above/below
    theme.button_height = 16 + 6 * 2  # font size + padding above/below
    theme.shadow_size = 140
    font_size = 8
    theme.set_for_theme(
        [
            (
                'View',
                [
                    ('normal', 'background_color', black_color),
                    ('focused', 'background_color', red_color),
                    ('selected', 'background_color', red_color),
                    ('normal', 'border_color', red_color),
                    ('normal', 'border_widths', 0),
                    ('normal', 'margin', (6, 6)),
                    ('normal', 'padding', (0, 0)),
                    ('normal', 'shadowed', False),
                ]
            ),
            (
                'Scene',
                [
                    ('normal', 'background_color', black_color)
                ]
            ),
            (
                'Label',
                [
                    ('normal', 'text_color', red_color),
                    ('selected', 'text_color', black_color),
                    ('normal', 'text_shadow_color', red_color),
                    ('normal', 'text_shadow_offset', (0, 1)),
                    ('normal', 'padding', (6, 6)),
                    ('normal', 'border_widths', None),
                    ('normal', 'font', resource.get_font(font_size)),
                ]
            ),
            (
                'Button',
                [
                    ('normal', 'background_color', black_color),
                    ('focused', 'background_color', red_color),
                    ('normal', 'text_color', red_color),
                    ('focused', 'text_color', black_color),
                    ('normal', 'font', resource.get_font(font_size, use_bold=True)),
                    ('normal', 'border_widths', 1),
                    ('normal', 'border_color', red_color),
                    ('normal', 'text_shadow_color', red_color),
                    ('normal', 'text_shadow_offset', (0, 1)),
                ]
            ),
            (
                'ImageButton',
                [
                    ('normal', 'background_color', black_color),
                    ('focused', 'background_color', red_color),
                    ('normal', 'border_color', red_color),
                    ('normal', 'border_widths', 1),
                    ('normal', 'padding', (6, 6)),
                ]
            ),
            (
                'ScrollbarThumbView',
                [
                    ('normal', 'background_color', black_color),
                    ('focused', 'background_color', red_color),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'ScrollbarView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'border_widths', (1, 1, 0, 0)),
                ]
            ),
            (
                'ScrollView',
                [
                    ('normal', 'hole_color', red_color),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'SliderTrackView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'value_color', red_color),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'SliderView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'border_widths', None),
                ]
            ),
            (
                'ImageView',
                [
                    ('normal', 'background_color', clear_color),
                    ('normal', 'padding', (0, 0)),
                ]
            ),
            (
                'Checkbox',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'padding', (0, 0)),
                    ('focused', 'check_label.background_color', red_color),
                    ('normal', 'check_label.border_widths', 1),
                    ('normal', 'label.background_color', clear_color),
                ]
            ),
            (
                'SpinnerView',
                [
                    ('normal', 'border_widths', None),
                ]
            ),
            (
                'DialogView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'shadowed', True),
                    ('normal', 'border_widths', 1),
                ]
            ),
            (
                'AlertView',
                [
                    ('normal', 'title_label.background_color', black_color),
                    ('normal', 'title_label.text_color', red_color),
                    ('normal', 'title_label.border_widths', 1),
                    ('normal', 'title_label.text_shadow_offset', None),
                    ('normal', 'message_label.background_color', clear_color),
                    ('normal', 'font', resource.get_font(font_size)),
                    ('normal', 'padding', (6, 6)),
                ]
            ),
            (
                'NotificationView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'border_color', red_color),
                    ('normal', 'border_widths', (0, 2, 2, 2)),
                    ('normal', 'padding', (0, 0)),
                    ('normal', 'message_label.background_color', clear_color),
                ]
            ),
            (
                'SelectView',
                [
                    ('normal', 'disclosure_triangle_color', black_color),
                    ('normal', 'border_widths', 1),
                    ('normal', 'top_label.focusable', False),
                ]
            ),
            (
                'TextField',
                [
                    ('focused', 'label.background_color', black_color),
                    ('focused', 'text_color', red_color),
                    ('normal', 'placeholder_text_color', red_color),
                    ('normal', 'border_widths', 1),
                    ('normal', 'text_color', red_color),
                    ('normal', 'background_color', black_color),
                    ('disabled', 'text_color', red_color),
                    ('normal', 'blink_cursor', True),
                    ('normal', 'cursor_blink_duration', 450),
                ]
            ),
            (
                'GridView',
                [
                    ('normal', 'background_color', black_color),
                    ('normal', 'line_color', red_color),
                ]
            )
        ]
    )
    return theme


def init():
    """Initialize theme support."""
    light = init_light_theme()
    dark = init_dark_theme()
    dracula_theme = init_dracula_theme()
    use_theme(dracula_theme)
