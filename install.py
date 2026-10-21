# Modified 2026-10-22 by weewx-packages: compatibility and tracker repairs.
# installer for cwxn
# Copyright 2014-2020 Matthew Wall
# Distributed under the terms of the GNU Public License (GPLv3)

from weecfg.extension import ExtensionInstaller

def loader():
    return CWXNInstaller()

class CWXNInstaller(ExtensionInstaller):
    def __init__(self):
        super(CWXNInstaller, self).__init__(
            version="0.6.1",
            name='cwxn',
            description='Emit a Cumulus wxnow.txt for LOOP data.',
            author="Matthew Wall",
            author_email="mwall@users.sourceforge.net",
            process_services='user.cwxn.CumulusWXNow',
            config={
                'CumulusWXNow' : {
                    'filename': '/var/tmp/wxnow.txt'}},
            files=[('bin/user', ['bin/user/cwxn.py'])]
            )
