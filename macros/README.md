This folder is intended for general purpose user macro scripts, for example for automation tasks,
to go to listen to radio presets, etc...

**(i) Also the control web page will look here:**

Any file here named like **`N_some_nice_name`** will be consider as an user macro
by the control web page, then a web button will be used to trigger the macro.

N determines the position into the web macros key pad.

For example

```
$ ls -1 ecapre/macros/
1_RNE
2_Radio_Clasica
3_Radio_3
7_Radio-OFF
README.md
```

Will show the following key pad layout:

```
    [      RNE       ]  [ Radio_Clasica ]  [    Radio_3    ]
    [      --        ]  [       --      ]  [      --       ]
    [   Radio-OFF    ]  [       --      ]  [      --       ]
```

**NOTICE:** if no macro files `N_xxxx` were defined under `~/ecpre/macros/`
then **NO keypad** will be displayed on the control web page.

