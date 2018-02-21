#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
C/C++ ZIP Generator
Copyright (C) 2012-2015, 2018 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

generate_c_zip.py: Generator for C/C++ ZIP

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys
import os
import shutil

sys.path.append(os.path.split(os.getcwd())[0])
import common

class CZipGenerator(common.ZipGenerator):
    def __init__(self, *args):
        common.ZipGenerator.__init__(self, *args)

        self.tmp_dir          = self.get_tmp_dir()
        self.tmp_source_dir   = os.path.join(self.tmp_dir, 'source')
        self.tmp_examples_dir = os.path.join(self.tmp_dir, 'examples')

    def get_bindings_name(self):
        return 'c'

    def prepare(self):
        common.recreate_dir(self.tmp_dir)
        os.makedirs(self.tmp_source_dir)
        os.makedirs(self.tmp_examples_dir)

    def generate(self, device):
        if not device.is_released():
            return

        # Copy device examples
        tmp_examples_device_dir = os.path.join(self.tmp_examples_dir,
                                               device.get_category().under,
                                               device.get_name().under)

        if not os.path.exists(tmp_examples_device_dir):
            os.makedirs(tmp_examples_device_dir)

        for example in common.find_device_examples(device, r'^example_.*\.c$'):
            shutil.copy(example[1], tmp_examples_device_dir)

    def finish(self):
        root_dir = self.get_root_dir()

        # Copy IP Connection examples
        for example in common.find_examples(root_dir, r'^example_.*\.c$'):
            shutil.copy(example[1], self.tmp_examples_dir)

        # Copy bindings and readme and merge symbols
        with open(os.path.join(root_dir, 'ip_connection.symbols'), 'r') as f:
            symbols = 'EXPORTS\n' + f.read()

        for filename in self.get_released_files():
            path = os.path.join(self.get_bindings_dir(), filename)

            if path.endswith('.symbols'):
                with open(path, 'r') as f:
                    symbols += f.read()
            else:
                shutil.copy(path, self.tmp_source_dir)

        with open(os.path.join(self.tmp_source_dir, 'tinkerforge.def'), 'w') as f:
            f.write(symbols)

        shutil.copy(os.path.join(root_dir, 'ip_connection.c'),              self.tmp_source_dir)
        shutil.copy(os.path.join(root_dir, 'ip_connection.h'),              self.tmp_source_dir)
        shutil.copy(os.path.join(root_dir, 'Makefile'),                     self.tmp_source_dir)
        shutil.copy(os.path.join(root_dir, 'changelog.txt'),                self.tmp_dir)
        shutil.copy(os.path.join(root_dir, 'readme.txt'),                   self.tmp_dir)
        shutil.copy(os.path.join(root_dir, '..', 'configs', 'license.txt'), self.tmp_dir)

        # Make zip
        self.create_zip_file(self.tmp_dir)

def generate(root_dir):
    common.generate(root_dir, 'en', CZipGenerator)

if __name__ == '__main__':
    generate(os.getcwd())
