# gdbg  

<img 
  title="gdbg logo"
  alt="red blood drop with text 'gdbg' centered"
  src="assets/gdbg_logo.png" 
  width="80"
/>

## overview

> gdbg: *get dexcom blood glucose*

a python app that displays blood glucose in the macos menu bar. retrieves blood glucose from dexcom via the [pydexcom](https://github.com/gagebenne/pydexcom) library. it also writes the blood glucose and trend arrow to a state file that can be used for displaying data in your terminal (or anything else you want).

this app was inspired by [kylebshr/luka-mini](https://github.com/kylebshr/luka-mini/tree/main). this is a *fantastic* app and would recommend for people who want a seamless app experience. i wanted to be able to access the blood glucose data outside of the app for other uses.

<img 
  title="menu bar app in use"
  alt="screenshot of menu bar app in use"
  src="assets/menu_bar.png" 
  width=500
/>

<img 
  title="blood sugar in terminal prompt"
  alt="screenshot of blood sugar in terminal prompt"
  src="assets/terminal_prompt.png" 
  width=500
/>

## how to use

1. download zip from [releases](https://github.com/GENERICERROR000/gdbg/releases)

2. unzip and move to `Applications folder`

3. setup credentials

*__this file must be created manually__*

* `~/.dexcom/dexcom_credentials.json`

```json
{
  "username" : "dexcom_username",
  "password": "dexcom_password"
}
```

4. run app or add it to your login items on mac

## blood glucose state file

this file is generated by the app

* `~/.dexcom/bg_status.txt`

format of the status is: `[bg] [delta] [trend arrow] '[reading timestamp]'`

the delta starts at 0 and will show change after second reading is retrieved.

### using in zsh $PROMPT

```sh
# ~/.zshrc

function get_bg() {
    RED='\033[91m'
    GREEN='\033[92m'
    YELLOW='\033[93m'
    END='\033[0m'

    state_file=$(cat $HOME/.dexcom/bg_status.txt)
    value=$(echo "$state_file" | cut -d' ' -f1)
    delta=$(echo "$state_file" | cut -d' ' -f2)
    arrow=$(echo "$state_file" | cut -d' ' -f3)

    if [[ $value -ge 80 && $value -le 180 ]]; then
        color="$GREEN"
    elif [[ $value -gt 180 ]]; then
        color="$YELLOW"
    elif [[ $value -lt 80 ]]; then
        color="$RED"
    fi

    echo "${color}${value} (${delta}) ${arrow}${END}"
}

# backslash in `\$(...)` is required for the value to update every time 
export PROMPT="$PROMPT\$(get_bg)"
```

## manually building app

using [anaconda](https://docs.anaconda.com/anaconda/install/mac-os/#command-line-install) on macos

```sh
# (1) create virtual environment
conda create --name gdbg python=3.11
conda activate gdbg

# (2) install requirements
pip install --no-cache-dir -r requirements.txt

# (3) build app
python setup.py py2app -A

# (4) run app from terminal to see errors
dist/gdbg.app/Contents/MacOS/gdbg
```

### known issues

when building, if you get the error that the library `libffi.8.dylib` is missing, you can install it with `brew`.

```sh
brew install libffi
```

## credits

assets

* logo by [izzy bulling - @izval](https://www.instagram.com/izval/)
* [modak](https://github.com/EkType/Modak) font used in logo

packages

* [gagebenne/pydexacom](https://github.com/gagebenne/pydexcom)
* [jaredks/rumps](https://github.com/jaredks/rumps)
* [dante-biase/py2app](https://github.com/dante-biase/py2app)

## references

* [kylebshr/luka-mini](https://github.com/kylebshr/luka-mini/tree/main)
* [Create a macOS Menu Bar App with Python (Pomodoro Timer) - Camillo Visini](https://camillovisini.com/coding/create-macos-menu-bar-app-pomodoro)
* [Glucose Readings in a Terminal Prompt - Hart Hoover](https://harthoover.com/glucose-readings-in-a-terminal-prompt/)

## TODO

1. [ ] on init, get 2 bg's so can calculate actual delta
  * currently shows huge increase on start...
2. [ ] linux version (branch:`gnome_extension`)
  * [ ] run `dexcom_handler.py` as service
  * [ ] create gnome top bar extension
  * [ ] use timestamp in state file for "last updated"
  * [ ] update readme
