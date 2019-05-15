#! /usr/bin/env python3

import simplefix

p = simplefix.FixParser()


f = open("secdef.dat")
for line in f:
    line = line.rstrip('\n')
    p.append_buffer(b'8=FIX.4.2\x01')
    p.append_buffer(line)
    p.append_buffer(b'10=000\x01')
    m = p.get_message()
    print(m)

f.close()
