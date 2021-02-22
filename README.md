# keyboard-switch

Simple, yet effective, script written in Python to change keyboard layout by using setxkbmap.

## Usage

```
usage: kbswitch [-h] [-n] [-p] [-s NAME] [-S N] [-a NAME] [-r NAME] [-R N] [-o FROM TO] [-c] [-l] [-d] [--notify]

optional arguments:
  -h, --help            show this help message and exit
  -n, --next            Next mapping
  -p, --previous        Previous mapping
  -s NAME, --set NAME   Set current mapping to NAME
  -S N, --set-number N  Set current mapping to NUMBER
  -a NAME, --add NAME   Add current mapping with name NAME
  -r NAME, --remove NAME
                        Remove mapping with name NAME
  -R N, --remove-number N
                        Remove mapping with order N
  -o FROM TO, --order FROM TO
                        Reorder mapping at place FROM to place TO
  -c, --current         Print current layout
  -l, --list            Lists layouts in order
  -d, --details         Print layouts in order with details
  --notify              Prints change to notification window using libnotify
```

### Example

#### Add layout
  
(Current layout is `gb(extd)`)

```sh
$ kbswitch -a gb_qwerty  # register current layout with name `gb_qwerty`
$ kbswitch -l  # list
+  0 gb_qwerty
```

> Changed layout to colemak

```sh
$ kbswitch -a gb_colemak  # register current layout with name `gb_colemak`
$ kbswitch -l  # list
+  0 gb_qwerty
   1 gb_colemak
```

Internally, the last mapping is still considered the current one because this program isn'tsynchronized to anything.

#### Switch layout

Using the last two registered layouts and starting under the gb QWERTY layout.

```sh
$ kbswitch -n  # next
$ kbswitch -l  # list
   0 gb_qwerty
+  1 gb_colemak
```

Voilà, switched ! We can also select a layout using it's name or ID:

```sh
$ kbswitch -l # initially
   0 gb_qwerty
+  1 gb_colemak
   2 fr_azerty
   3 fr_colemak
$ kbswitch -s fr_colemak  # select with name
$ kbswitch -l
   0 gb_qwerty
   1 gb_colemak
   2 fr_azerty
+  3 fr_colemak
```

Equivalently:

```sh
$ kbswitch -S 3 # select with position
  ```

#### Reorder
  
```sh
$ kbswitch -l  # initially
   0 gb_qwerty
   1 gb_colemak
   2 fr_azerty
+  3 fr_colemak
$ kbswitch -o 2 1  # reorder 2 -> 1 (put `fr_azerty` at place 1)
$ kbswitch -l  # result
   0 gb_qwerty
   1 fr_azerty
   2 gb_colemak
+  3 fr_colemak
```

#### Remove

```sh
$ kbswitch -l  # initially
   0 gb_qwerty
   1 fr_azerty
   2 gb_colemak
+  3 fr_colemak
$ kbswitch -r fr_azerty  # remove by name
$ kbswitch -l  # result
   0 gb_qwerty
   1 gb_colemak
+  2 fr_colemak
```

Equivalently:

```sh
$ kbswitch -R 2  # Remove by position
```

#### Print
  
- __Names in order__:

```sh
$ kbswitch -l  # print
+  0 gb_qwerty
   1 gb_colemak
   2 fr_colemak
```

- __Current layout with options, variants, etc...__:

```sh
$ kbswitch -c  # current
gb_qwerty
  model:        pc
  layout:       gb
  variant:      extd
  options:
```

- __All registered layouts with the above informations__:

```sh
$ kbswitch -d  # details
gb_qwerty
  model:        pc
  layout:       gb
  variant:      extd
  options:
gb_colemak
  model:        pc105
  layout:       gb(cmk_ed_us)
  variant:
  options:      misc:extend,lv5:caps_switch_lock,grp:shifts_toggle,compose:menu,misc:cmk_curl_dh
fr_colemak
  model:        pc105
  layout:       fr(cmk_ed_us)
  variant:
  options:      misc:extend,lv5:caps_switch_lock,grp:shifts_toggle,compose:menu,misc:cmk_curl_dh
```  


#### Notification

If you want to have a notification of a layout switch via `libnotify`, you may add the argument `--notify`.

```sh
$ kbswitch -n --notify  # changes to next layout and sends a notification
```