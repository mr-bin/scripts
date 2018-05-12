#! /usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4
"""
vnote2txt - converts vNote files (e.g. from Galaxy S2 Memo app) to text

Windows users - please install Python from www.python.org

Can be double-clicked or run without arguments to show a file chooser
Or can be run from the commandline, e.g. python ./vnote2txt /home/user/docs/*.vn
"""

from __future__ import print_function
import sys
import quopri
import re
import unittest

def wait_for_exit():
    sys.stdout.write("\n")
    if sys.hexversion >= 0x030000F0:
        input("Press Enter to exit...")
    else:
        raw_input("Press Enter to exit...")

if sys.version_info < (2,7):
    print ("this script has been tested with Python 2.7.2 and Python 3.2.2 - please install a newer version of Python")
    wait_for_exit()
    sys.exit()

"""
Displays a graphical Open Files dialog
"""
def choose_files():
    if sys.hexversion >= 0x030000F0:
        import tkinter.filedialog as filedialog
        string_type = str
    else:
        import tkFileDialog as filedialog
        string_type = basestring

    options = {}
    options['filetypes'] = [('vnote files', '.vnt') ,('all files', '.*')]
    options['multiple'] = 1
    filenames = filedialog.askopenfilename(**options)
    #print ("filenames are ", type(filenames), filenames)
    if isinstance(filenames, string_type):
        # tkinter is not converting the TCL list into a python list...
        # see http://stackoverflow.com/questions/9227859/
        #
        # based on suggestion by Cameron Laird in http://bytes.com/topic/python/answers/536853-tcl-list-python-list
        if sys.hexversion >= 0x030000F0:
            import tkinter
        else:
            import Tkinter as tkinter
        tk_eval = tkinter.Tk().tk.eval
        tcl_list_length = int(tk_eval("set tcl_list {%s}; llength $tcl_list" % filenames))
        filenames = [] # change to a list
        for i in range(tcl_list_length):
            filenames.append(tk_eval("lindex $tcl_list %d" % i))
        #print ("filenames are now", filenames)
    return filenames

line_pattern = re.compile('([A-Z-]+);?([^:]*):(.*)') # e.g. BODY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:some note

"""
Extracts the keys, values and metadata from a vnote file
"""
def parse_file(f):
    values = {}
    metadata = {}
    prevline = None
    for line in f.readlines():
        # merge quoted-printable soft newlines e.g.
        # BEGIN:VCARD
        # BODY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=12=34=
        # =56
        # END:VCARD
        if prevline:
            line = prevline + line
        prevline = None

        # parse vcard properties
        parts = line_pattern.findall(line.strip())
        if len(parts) == 0:
            print ("unable to parse line: " + line)
            return None,None
        else:
            parts = parts[0]
        key = parts[0]
        if len(parts) == 2:
            values[key] = parts[1]
        elif len(parts) == 3:
            values[key] = parts[2]
            propdict = metadata.setdefault(key, {})
            for prop in parts[1].split(';'):
                if len(prop) > 0:
                    k, v = prop.split('=')
                    propdict[k] = v

            if propdict.get('ENCODING') == 'QUOTED-PRINTABLE' and values[key].endswith('='):
                prevline = line.rstrip()[:-1] # reparse

        else:
            print ("unable to parse line: " + line)
            return None,None

    return values, metadata

"""
Returns the content (i.e. the BODY property) of a vnote file, and an error message
"""
def process_file(f):
    values, metadata = parse_file(f)

    # TODO: more integrity checking of the file
    if values is None:
        return None, None
    elif values['BEGIN'] != 'VNOTE' or values['END'] != 'VNOTE' or values['VERSION'] != '1.1':
        return None, "is not a valid vNote 1.1 file"
    else:
        body = values['BODY']
        if metadata['BODY'].get('ENCODING') == 'QUOTED-PRINTABLE':

            # add end-of-line
            if len(body) > 0 and body[-1] != '\n':
                body += '\r\n'

            # decode quoted-printable
            if sys.hexversion >= 0x030000F0:
                body = body.encode('utf8')
            body = quopri.decodestring(body, header=False)


        return body, None

class Tests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_expected_output(self):
        for filename in ['2011-11-19.15.59.21.vnt', 'all-quoted.vnt', 'colon.vnt', 'euro-and-accents.vnt', 'with-newline.vnt']:
            if sys.hexversion >= 0x030000F0:
                encoding = { 'encoding' : 'utf8' }
            else:
                encoding = {}

            with open('tests/' + filename, 'r', **encoding) as f:
                body, error = process_file(f)
                self.assertIsNone(error)
                expected = None
                with open('tests/' + filename + '.txt', 'rb') as g:
                    expected = g.read()
                self.assertEqual(body, expected, "unexpected output for " + filename)

                if sys.hexversion >= 0x030000F0:
                    import io
                    io.BytesIO().write(body) # ensure we don't get the 'str' does not support the buffer interface error

    def test_bad_version(self):
        for filename in ['bad-version.vnt']:
            with open('tests/' + filename, 'r') as f:
                body, error = process_file(f)
                self.assertIsNone(body)
                self.assertEqual(error, "is not a valid vNote 1.1 file")

if __name__ == "__main__":
    filenames = sys.argv[1:]
    if len(filenames) == 0:
        filenames = choose_files()

    if len(filenames) == 0:
        print ("no files to convert")
    else:
        print ("converting", filenames, "(", type(filenames), ")")

    errors = False

    for filename in filenames:
        with open(filename, 'r', encoding='utf8') as f:
            sys.stdout.write(filename + ": ")

            body, error = process_file(f)
            if body is None:
                errors = True
                if error is None:
                    sys.stdout.write("error\n")
                else:
                    sys.stdout.write(error + "\n")
            else:
                with open(filename + '.txt', 'wb') as out:
                    out.write(body)
                sys.stdout.write("converted\n")

    if errors:
        wait_for_exit()
