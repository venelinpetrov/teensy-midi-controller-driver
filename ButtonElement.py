from _Framework.ButtonElement import ON_VALUE, OFF_VALUE, ButtonElement as ButtonElementBase

class ButtonElement(ButtonElementBase):
    _on_value = None
    _off_value = None

    def reset(self):
        self._on_value = None
        self._off_value = None
        super(ButtonElement, self).reset()
        return

    def set_on_off_values(self, on_value, off_value):
        self._on_value = on_value
        self._off_value = off_value
