from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.MixerComponent import MixerComponent as MixerComponentBase

class MixerComponent(MixerComponentBase):
    next_sends_button = ButtonControl()
    prev_sends_button = ButtonControl()

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._update_send_buttons()

    def set_send_controls(self, controls):
        self._send_controls = controls
        for index, channel_strip in enumerate(self._channel_strips):
            if self.send_index is None:
                channel_strip.set_send_controls([None])
            else:
                send_controls = [ controls.get_button(index, i) for i in xrange(2) ] if controls else [None]
                skipped_sends = [ None for _ in xrange(self.send_index) ]
                channel_strip.set_send_controls(skipped_sends + send_controls)
        return

    def _get_send_index(self):
        return super(MixerComponent, self)._get_send_index()

    def _set_send_index(self, index):
        if index is not None and index % 2 > 0:
            index -= 1
        super(MixerComponent, self)._set_send_index(index)
        self._update_send_buttons()
        return

    send_index = property(_get_send_index, _set_send_index)

    def _update_send_buttons(self):
        self.next_sends_button.enabled = self.send_index is not None and self.send_index < self.num_sends - 2
        self.prev_sends_button.enabled = self.send_index is not None and self.send_index > 0
        return

    @next_sends_button.pressed
    def next_sends_button(self, button):
        self.send_index = min(self.send_index + 2, self.num_sends - 1)

    @prev_sends_button.pressed
    def prev_sends_button(self, button):
        self.send_index = max(self.send_index - 2, 0)

    def set_track_select_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if strip != None:
                strip.set_select_button(button)
