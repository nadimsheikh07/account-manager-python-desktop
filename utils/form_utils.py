# utils/form_utils.py


def set_error(is_error: bool, widget):
    """
    Set or clear error state on a widget using Qt property.
    Requires global stylesheet to style [error="true"].
    """
    widget.setProperty("error", is_error)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
