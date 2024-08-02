from __future__ import unicode_literals

import sys
from typing import Optional, Sequence, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import (KeyBindings,
                                                     merge_key_bindings)
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Label, RadioList

DEFAULT_PROMPT_SYLE = Style.from_dict(
    {
        # Default style.
        "": "#56B6C2",
        "question": "ansigray",
        "question_mark": "#98C379 bold",
    }
)


def radiolist_prompt(
    title: Union[str, AnyFormattedText] = "",
    values: Sequence[Tuple[str, AnyFormattedText]] = None,
    default: Optional[str] = None,
    cancel_value: Optional[str] = None,
    style: Optional[Style] = DEFAULT_PROMPT_SYLE,
) -> str:
    """
    Custom prompt for selecting a value from a list of values.

    Kudos to: https://github.com/prompt-toolkit/python-prompt-toolkit/issues/756#issuecomment-1294742392

    Args:
        title (`Union[str, AnyFormattedText]`): prompt title
        values (`Sequence[Tuple[str, AnyFormattedText]]`): list of values to select from
        default (`Optional[str]`): default value
        cancel_value (`Optional[str]`): value to return if the user cancels the prompt
        style (`Optional[Style]`): prompt style

    Returns:
        selected value
    """
    # Create the radio list
    radio_list = RadioList(values, default)
    # Remove the enter key binding so that we can augment it
    radio_list.control.key_bindings.remove("enter")

    bindings = KeyBindings()

    # Replace the enter key binding to select the value and also submit it
    @bindings.add("enter")
    def exit_with_value(event):
        """
        Pressing Enter will exit the user interface, returning the highlighted value.
        """
        radio_list._handle_enter()
        event.app.exit(result=radio_list.current_value)

    @bindings.add("c-c")
    def backup_exit_with_value(event):
        """
        Pressing Ctrl-C will exit the user interface with the cancel_value.
        """
        event.app.exit(result=cancel_value)

    # Create and run the mini inline application
    application = Application(
        layout=Layout(HSplit([Label(title), radio_list])),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=False,
    )

    return application.run()


def get_multiline_input_save_keyboard() -> str:
    """
    Based on the OS, return the keyboard key combination to save multiline input

    Returns:
        keyboard key combination
    """
    is_windows = sys.platform.startswith("win")
    is_mac = sys.platform.startswith("darwin")

    if is_windows:
        return "[Alt+Enter]"
    elif is_mac:
        return "[Option+Enter]"

    return "[Meta+Enter]"
