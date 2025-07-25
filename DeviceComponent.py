import Live
from _Framework.Control import control_list, ButtonControl
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase
from _Framework.ModesComponent import EnablingModesComponent, tomode

class DeviceComponent(DeviceComponentBase):
    prev_device_button = ButtonControl(color='DefaultButton.On')
    next_device_button = ButtonControl(color='DefaultButton.On')

    @prev_device_button.pressed
    def prev_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    @next_device_button.pressed
    def next_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def set_device(self, device):
        super(DeviceComponent, self).set_device(device)

    def set_bank_buttons(self, buttons):
        super(DeviceComponent, self).set_bank_buttons(buttons)

    def _is_banking_enabled(self):
        return True


class DeviceModeComponent(EnablingModesComponent):
    device_mode_button = ButtonControl()

    def __init__(self, device_settings_mode = None, *a, **k):
        super(DeviceModeComponent, self).__init__(*a, **k)
        #raise device_settings_mode is not None or AssertionError
        self._device_settings_mode = tomode(device_settings_mode)
        return

    @device_mode_button.released_immediately
    def device_mode_button(self, button):
        self.cycle_mode()

    @device_mode_button.pressed_delayed
    def device_mode_button(self, button):
        self.selected_mode = 'enabled'
        self._device_settings_mode.enter_mode()

    @device_mode_button.released_delayed
    def device_mode_button(self, button):
        self._device_settings_mode.leave_mode()

    def _update_buttons(self, selected_mode):
        super(DeviceModeComponent, self)._update_buttons(selected_mode)