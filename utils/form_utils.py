# ==============================
# Error Styling Helpers
# ==============================
def set_error(error, widget):
    widget.setProperty("error", error)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
