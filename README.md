# MIDI Mapping for Ableton Live 9.6.2

## Developing (Windows)

1. Go to `\ProgramFiles\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts`
2. Clone this repo
3. Choose Option/Preferences...
4. Choose Teensy Control Surface and set it as Input and Output device

![al_teensy_props](https://cloud.githubusercontent.com/assets/3126733/20649788/bb699ac4-b4cf-11e6-863a-82a106e7a197.png)

5.Now the device shoud send and receive MIDI message from Live

## Debugging (Windows)

1. Stop Ableton Live
2. Go to `\Users\[username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\Log.txt`
3. Delete it
4. Start Ableton Live
5. `Log.txt` was created, open it
6. Search for `RemoteScriptError`
