#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shell Documentation Generator
Copyright (C) 2012-2013 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011-2013 Olaf Lüke <olaf@tinkerforge.com>

generator_shell_doc.py: Generator for Shell documentation

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
import subprocess
import glob
import re

sys.path.append(os.path.split(os.getcwd())[0])
import common
import shell_common

device = None

def format_doc(packet):
    text = common.select_lang(packet.get_doc()[1])
    device_name = device.get_shell_device_name()
    constants = {'en': 'symbols', 'de': 'Symbole'}

    for other_packet in device.get_packets():
        name_false = ':func:`{0}`'.format(other_packet.get_camel_case_name())
        name_right = ':sh:func:`{1} <{0} {1}>`'.format(device_name, other_packet.get_underscore_name().replace('_', '-'))
        text = text.replace(name_false, name_right)

    text = common.handle_rst_word(text)
    text = common.handle_rst_if(text, device)

    def constant_format(prefix, constant, definition, value):
        c = '* ``{0}`` = {1}, '.format(definition.name_underscore.replace('_', '-'), value)

        for_ = {
        'en': 'for',
        'de': 'für'
        }

        c += common.select_lang(for_) + ' '

        e = []
        for element in constant.elements:
            name = element.get_dash_name()
            if element.get_direction() == 'in':
                e.append('<{0}>'.format(name))
            else:
                e.append(name)

        if len(e) > 1:
            and_ = {
            'en': 'and',
            'de': 'und'
            }

            c += ', '.join(e[:-1]) + ' ' + common.select_lang(and_) + ' ' + e[-1]
        else:
            c += e[0]

        return c + '\n'

    text += common.format_constants('', packet, constants_name=constants,
                                    char_format='{0}',
                                    constant_format_func=constant_format)

    text += common.format_since_firmware(device, packet)

    return common.shift_right(text, 1)

def make_examples(generator):
    def title_from_file_name(file_name):
        file_name = file_name.replace('example-', '').replace('.sh', '').replace('-', '_')
        return common.underscore_to_space(file_name)

    return common.make_rst_examples(title_from_file_name, device, generator.get_bindings_root_directory(),
                                    'shell', 'example-', '.sh', 'Shell', 'bash')

def make_parameter_desc(packet):
    desc = '\n'
    param = ' :param <{0}>: {1}'
    has_symbols = {
    'en': 'has symbols',
    'de': 'hat Symbole'
    }

    for element in packet.get_elements('in'):
        t = element.get_shell_type()
        desc += param.format(element.get_dash_name(), t)

        if element.has_constants():
            desc += ' ({0})'.format(common.select_lang(has_symbols))

        desc += '\n'

    return desc

def make_return_desc(packet):
    nothing = {
    'en': 'no output',
    'de': 'keine Ausgabe'
    }
    has_symbols = {
    'en': 'has symbols',
    'de': 'hat Symbole'
    }
    elements = packet.get_elements('out')

    if len(elements) == 0:
        return '\n :noreturn: {0}\n'.format(common.select_lang(nothing))

    ret = '\n'
    for element in elements:
        t = element.get_shell_type()
        ret += ' :returns {0}: {1}'.format(element.get_dash_name(), t)

        if element.has_constants() or \
           packet.get_function_id() == 255 and element.get_underscore_name() == 'device_identifier':
            ret += ' ({0})'.format(common.select_lang(has_symbols))

        ret += '\n'

    return ret

def make_methods(typ):
    methods = ''
    func_start = '.. sh:function:: '
    device_name = device.get_shell_device_name()
    for packet in device.get_packets('function'):
        if packet.is_virtual():
            continue

        if packet.get_doc()[0] != typ:
            continue
        name = packet.get_underscore_name().replace('_', '-')
        params = shell_common.make_parameter_list(packet)
        pd = make_parameter_desc(packet)
        r = make_return_desc(packet)
        d = format_doc(packet)
        desc = '{0}{1}{2}'.format(pd, r, d)
        func = '{0}tinkerforge call {1} <uid> {2} {3} \n{4}'.format(func_start,
                                                                    device_name,
                                                                    name,
                                                                    params,
                                                                    desc)
        methods += func + '\n'

    return methods

def make_callbacks():
    cbs = ''
    func_start = '.. sh:function:: '
    device_name = device.get_shell_device_name()
    for packet in device.get_packets('callback'):
        if packet.is_virtual():
            continue

        param_desc = make_return_desc(packet)
        desc = format_doc(packet)

        func = '{0} tinkerforge dispatch {1} <uid> {2}\n{3}\n{4}'.format(func_start,
                                                                         device_name,
                                                                         packet.get_underscore_name().replace('_', '-'),
                                                                         param_desc,
                                                                         desc)
        cbs += func + '\n'

    return cbs

def make_api():
    c_str = {
    'en': """
.. _{1}_{2}_shell_callbacks:

Callbacks
^^^^^^^^^

Callbacks can be used to receive time critical or recurring data from the
device:

.. code-block:: bash

    tinkerforge dispatch {3} <uid> example

The available callbacks are described below.

.. note::
 Using callbacks for recurring events is *always* preferred
 compared to using getters. It will use less USB bandwidth and the latency
 will be a lot better, since there is no round trip time.

{0}
""",
    'de': """
.. _{1}_{2}_shell_callbacks:

Callbacks
^^^^^^^^^

Callbacks können registriert werden um zeitkritische oder wiederkehrende Daten
vom Gerät zu erhalten:

.. code-block:: bash

    tinkerforge dispatch {3} <uid> example

Die verfügbaren Callbacks werden weiter unten beschrieben.

.. note::
 Callbacks für wiederkehrende Ereignisse zu verwenden ist
 *immer* zu bevorzugen gegenüber der Verwendung von Abfragen.
 Es wird weniger USB-Bandbreite benutzt und die Latenz ist
 erheblich geringer, da es keine Paketumlaufzeit gibt.

{0}
"""
    }

    api = {
    'en': """
{0}
API
---

Possible exit codes for all ``tinkerforge`` commands are:

* 1: interrupted (ctrl+c)
* 2: syntax error
* 21: Python 2.5 or newer is required
* 22: Python ``argparse`` module is missing
* 23: socket error
* 24: other exception
* 25: invalid placeholder in format string
* 201: timeout occurred
* 209: invalid argument value
* 210: function is not supported
* 211: unknown error

{1}

Command Structure
^^^^^^^^^^^^^^^^^

.. sh:function:: X Stinkerforge Pcall N{3} A[<option>..] L<uid> L<function> L[<argument>..]

 :param <uid>: string
 :param <function>: string

 The ``call`` command is used to call a function of the {4}. It can take several
 options:

 * ``--help`` shows help for the specific ``call`` command and exits
 * ``--list-functions`` shows a list of known functions of the {4} and exits


.. sh:function:: X Stinkerforge Pdispatch N{3} A[<option>..] L<uid> L<callback>

 :param <uid>: string
 :param <callback>: string

 The ``dispatch`` command is used to dispatch a callback of the {4}. It can
 take several options:

 * ``--help`` shows help for the specific ``dispatch`` command and exits
 * ``--list-callbacks`` shows a list of known callbacks of the {4} and exits


.. sh:function:: X Stinkerforge Scall P{3} L<uid> N<function> A[<option>..] L[<argument>..]

 :param <uid>: string
 :param <function>: string

 The ``<function>`` to be called can take different options depending of its
 kind. All functions can take the following options:

 * ``--help`` shows help for the specific function and exits

 Getter functions can take the following options:

 * ``--execute <command>`` shell command line to execute for each incoming
   response (see section about :ref:`output formatting <ipcon_shell_output>`
   for details)

 Setter functions can take the following options:

 * ``--expect-response`` requests response and waits for it

 The ``--expect-response`` option for setter functions allows to detect
 timeouts and other error conditions calls of setters as well. The device will
 then send a response for this purpose. If this option is not given for a
 setter function then no response is send and errors are silently ignored,
 because they cannot be detected.


.. sh:function:: X Stinkerforge Sdispatch P{3} L<uid> N<callback> A[<option>..]

 :param <uid>: string
 :param <callback>: string

 The ``<callback>`` to be dispatched can take several options:

 * ``--help`` shows help for the specific callback and exits
 * ``--execute <command>`` shell command line to execute for each incoming
   response (see section about :ref:`output formatting <ipcon_shell_output>`
   for details)


{2}
""",
    'de': """
{0}
API
---

Mögliche Exit Codes für alle ``tinkerforge`` Befehle sind:

* 1: Unterbrochen (Ctrl+C)
* 2: Syntaxfehler
* 21: Python 2.5 oder neuer wird benötigt
* 22: Python ``argparse`` Modul fehlt
* 23: Socket-Fehler
* 24: Andere Exception
* 25: Ungültiger Platzhalter in Format-String
* 201: Timeout ist aufgetreten
* 209: Ungültiger Argumentwert
* 210: Funktion wird nicht unterstützt
* 211: Unbekannter Fehler

{1}

Befehlsstruktur
^^^^^^^^^^^^^^^

.. sh:function:: X Stinkerforge Pcall N{3} A[<option>..] L<uid> L<function> L[<argument>..]

 :param <uid>: string
 :param <function>: string

 Der ``call`` Befehl wird verwendet um eine Funktion des {4}s aufzurufen. Der
 Befehl kennt mehrere Optionen:

 * ``--help`` zeigt Hilfe für den spezifischen ``call`` Befehl an und endet dann
 * ``--list-functions`` zeigt eine Liste der bekannten Funktionen des {4}s an
   und endet dann


.. sh:function:: X Stinkerforge Pdispatch N{3} A[<option>..] L<uid> L<callback>

 :param <uid>: string
 :param <callback>: string

 Der ``dispatch`` Befehl wird verwendet um eingehende Callbacks des {4}s
 abzufertigen. Der Befehl kennt mehrere Optionen:

 * ``--help`` zeigt Hilfe für den spezifischen ``dispatch`` Befehl an und endet
   dann
 * ``--list-callbacks`` zeigt eine Liste der bekannten Callbacks des {4}s an
   und endet dann


.. sh:function:: X Stinkerforge Scall P{3} L<uid> N<function> A[<option>..] L[<argument>..]

 :param <uid>: string
 :param <function>: string

 Abhängig von der Art der aufzurufenden ``<function>`` kennt diese verschiedene
 Optionen. Alle Funktionen kennen die folgenden Optionen:

 * ``--help`` zeigt Hilfe für die spezifische ``<function>`` an und endet dann

 Getter-Funktionen kennen zusätzlich die folgenden Optionen:

 * ``--execute <command>`` Shell-Befehl der für jede eingehende Antwort
   ausgeführt wird (siehe den Abschnitt über :ref:`Ausgabeformatierung
   <ipcon_shell_output>` für Details)

 Setter-Funktionen kennen zusätzlich die folgenden Optionen:

 * ``--expect-response`` fragt Antwort an und wartet auf diese

 Mit der ``--expect-response`` Option für Setter-Funktionen können Timeouts und
 andere Fehlerfälle auch für Aufrufe von Setter-Funktionen detektiert werden.
 Das Gerät sendet dann eine Antwort extra für diesen Zweck. Wenn diese Option
 für eine Setter-Funktion nicht angegeben ist, dann wird keine Antwort vom
 Gerät gesendet und Fehler werden stillschweigend ignoriert, da sie nicht
 detektiert werden können.


.. sh:function:: X Stinkerforge Sdispatch P{3} L<uid> N<callback> A[<option>..]

 :param <uid>: string
 :param <callback>: string

 Der abzufertigende ``<callback>`` kennt mehrere Optionen:

 * ``--help`` zeigt Hilfe für den spezifische ``<callback>`` an und endet dann
 * ``--execute <command>`` Shell-Befehlszeile der für jede eingehende Antwort
   ausgeführt wird (siehe den Abschnitt über :ref:`Ausgabeformatierung
   <ipcon_shell_output>` für Details)

{2}
"""
    }

    bf = make_methods('bf')
    af = make_methods('af')
    ccf = make_methods('ccf')
    c = make_callbacks()
    api_str = ''
    if bf:
        api_str += common.select_lang(common.bf_str).format('', bf)
    if af:
        api_str += common.select_lang(common.af_str).format(af)
    if c:
        api_str += common.select_lang(common.ccf_str).format('', ccf)
        api_str += common.select_lang(c_str).format(c, device.get_underscore_name(),
                                                    device.get_category().lower(),
                                                    device.get_shell_device_name())

    ref = '.. _{0}_{1}_shell_api:\n'.format(device.get_underscore_name(),
                                            device.get_category().lower())

    return common.select_lang(api).format(ref, device.get_api_doc(), api_str,
                                          device.get_shell_device_name(),
                                          device.get_display_name() + ' ' + device.get_category())

class ShellDocGenerator(common.DocGenerator):
    def get_device_class(self):
        return shell_common.ShellDevice

    def get_element_class(self):
        return shell_common.ShellElement

    def generate(self, device_):
        global device
        device = device_

        title = { 'en': 'Shell bindings', 'de': 'Shell Bindings' }
        file_name = '{0}_{1}_Shell.rst'.format(device.get_camel_case_name(), device.get_category())

        rst = open(os.path.join(self.get_bindings_root_directory(), 'doc', common.lang, file_name), 'wb')
        rst.write(common.make_rst_header(device, 'shell', 'Shell'))
        rst.write(common.make_rst_summary(device, common.select_lang(title), 'shell'))
        rst.write(make_examples(self))
        rst.write(make_api())
        rst.close()

def generate(bindings_root_directory, lang):
    common.generate(bindings_root_directory, lang, ShellDocGenerator, True)

if __name__ == "__main__":
    for lang in ['en', 'de']:
        print("=== Generating %s ===" % lang)
        generate(os.getcwd(), lang)
