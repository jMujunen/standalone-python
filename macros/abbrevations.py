#!/usr/bin/env  python3

#  abbrevations.py - Keyboard abbrevation shortcuts

import os, sys, subprocess

try:

    import keyboard

    address = ['36426', 'Cardiff', 'Pl', 'Abbotsford', 'BC', 'V3G  3G4']

    print('Starting...')
    # Python shebang
    keyboard.add_abbreviation('####', '#!/usr/bin/env  python3')

    # Bash shebang
    keyboard.add_abbreviation('#bash', '#!/bin/bash')

    # Email addr
    keyboard.add_abbreviation('@@', 'joona.mujunen@gmail.com')

    # pword 
    keyboard.add_abbreviation(';;', 'kakkanapa')
    keyboard.add_abbreviation(';;;', 'kakkanapa25565')
    '''
    # Home addr
    # 36426 Cardiff Pl, Abbotsford, BC V3G 3G4
    keyboard.add_abbreviation('@street', 'V3G3G4')
    keyboard.add_abbreviation('@addr', '36426  Cardiff Pl  Abbotsford  BC')
    keyboard.add_abbreviation('@street1', 'kakkanapa  gihaiogha  uihguiahguhia') 
    '''
    # WAN IP
    keyboard.add_abbreviation('@ip', '184.65.126.196 ')
    
    keyboard.wait()

except ImportError:
    run_as_root = subprocess.run(
        f'sudo python3 {sys.argv[0]}',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if run_as_root.stderr:
        print(run_as_root.stderr)
        sys.exit(1)
except KeyboardInterrupt:
    print('Bye!')
    sys.exit(0)

