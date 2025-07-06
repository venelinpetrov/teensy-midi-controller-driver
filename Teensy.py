from __future__ import with_statement
from functools import partial
from itertools import chain
import Live
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurface import ControlSurface
from _Framework.EncoderElement import EncoderElement
from _Framework.IdentifiableControlSurface import IdentifiableControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import ModeButtonBehaviour, ModesComponent, AddLayerMode
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
from _Framework import Task
from .ButtonElement import ButtonElement
from .DeviceComponent import DeviceComponent, DeviceModeComponent
from .MixerComponent import MixerComponent
from .MidiMappings import *

NUM_TRACKS = 2
LIVE_CHANNEL = 0

class Teensy(ControlSurface):
    __module__=__name__
    __doc__= "Teensy midi mapping for Ableton 9"

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.__c_instance = c_instance
            self._create_controls()
            self._create_components()

    def _create_components(self):

        mixer = self._create_mixer()
        session = self._create_session()
        device = self._create_device()
        session.set_mixer(mixer)
        self.set_device_component(device)

    def _create_controls(self):
        def make_button(identifier, name, midi_type = MIDI_CC_TYPE):
            return ButtonElement(True, midi_type, LIVE_CHANNEL, identifier, name=name)

        def make_button_list(identifiers, name):
            return [ make_button(identifier, name % (i + 1), MIDI_NOTE_TYPE) for i, identifier in enumerate(identifiers) ]

        def make_encoder(identifier, name):
            return EncoderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, Live.MidiMap.MapMode.absolute, name=name)

        def make_slider(identifier, name):
            return SliderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, name=name)

        self._send_encoders = ButtonMatrixElement(rows=[[ make_encoder(SEND_CC + i, 'Top_Send_%d' % (i + 1)) for i in xrange(NUM_TRACKS) ], [ make_encoder(40 + NUM_TRACKS + i, 'Bottom_Send_%d' % (i + 1)) for i in xrange(NUM_TRACKS) ]])
        self._pan_device_encoders = ButtonMatrixElement(rows=[[ make_encoder(PAN_CC + i, 'Pan_Device_%d' % (i + 1)) for i in xrange(NUM_TRACKS) ]])
        self._volume_faders = ButtonMatrixElement(rows=[[ make_slider(VOLUME_CC + i, 'Volume_%d' % (i + 1)) for i in xrange(NUM_TRACKS) ]])
        self._pan_device_mode_button = make_button(DEVICE_MODE_CC, 'Pan_Device_Mode', MIDI_NOTE_TYPE)

        self._up_button = make_button(SEND_UP_CC, 'Up')
        self._down_button = make_button(SEND_DOWN_CC, 'Down')
        self._left_button = make_button(DEVICE_LEFT_CC, 'Track_Left')
        self._right_button = make_button(DEVICE_RIGHT_CC, 'Track_Right')
        self._select_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(64, 68), xrange(68, 72)), 'Track_Select_%d')])
        self._state_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(73, 77), xrange(89, 93)), 'Track_State_%d')])

    def _create_mixer(self):
        mixer = MixerComponent(NUM_TRACKS, is_enabled=True, auto_name=True)
        mixer.layer = Layer(track_select_buttons=self._select_buttons, send_controls=self._send_encoders, next_sends_button=self._down_button, prev_sends_button=self._up_button, pan_controls=self._pan_device_encoders, volume_controls=self._volume_faders)
        mixer.on_send_index_changed = partial(self._show_controlled_sends_message, mixer)

        return mixer

    def _create_session(self):
        session = SessionComponent(num_tracks=NUM_TRACKS, is_enabled=True, auto_name=True, enable_skinning=False)
        session.layer = Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button)
        self._on_session_offset_changed.subject = session
        return session

    @subject_slot('offset')
    def _on_session_offset_changed(self):
        session = self._on_session_offset_changed.subject
        self._show_controlled_tracks_message(session)

    def _create_device(self):
        device = DeviceComponent(name='Device_Component', is_enabled=False, device_selection_follows_track_selection=True)
        device.layer = Layer(parameter_controls=self._pan_device_encoders, priority=1)
        device_settings_layer = Layer(bank_buttons=self._state_buttons, prev_device_button=self._left_button, next_device_button=self._right_button, priority=1)
        mode = DeviceModeComponent(component=device, device_settings_mode=[AddLayerMode(device, device_settings_layer)], is_enabled=True)
        mode.layer = Layer(device_mode_button=self._pan_device_mode_button)
        return device

    def _show_controlled_sends_message(self, mixer):
        if mixer.send_index is not None:
            send_index = mixer.send_index
            send_name1 = chr(ord('A') + send_index)
            if send_index + 1 < mixer.num_sends:
                send_name2 = chr(ord('A') + send_index + 1)
                self.show_message('Controlling Send %s and %s' % (send_name1, send_name2))
            else:
                self.show_message('Controlling Send %s' % send_name1)
        return

    def _show_controlled_tracks_message(self, session):
        start = session.track_offset() + 1
        end = min(start + NUM_TRACKS, len(session.tracks_to_use()))
        if start < end:
            self.show_message('Controlling Track %d to %d' % (start, end))
        else:
            self.show_message('Controlling Track %d' % start)