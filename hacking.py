import re
import sys

def chm_html_to_md(filename):
    with open(filename, 'r') as f:
        data = f.read()

    reError = re.compile('^\s+Error \#\d+:.*$')
    reTableBreak = re.compile('^\s*\+[+-]+\+$')
    reTableRow = re.compile('^\s*\|.+\|$')
    reHeadingBreak = re.compile('^\s+\+\-+$')
    reHeadingRow = re.compile('^\s+\|.*$')
    reMemoryLine = re.compile('^[0-9A-F]{4}:\s+.*$')
    reJumpFrom = re.compile('^Jump from \$.*$')
    reJumpFromNext = re.compile('^\s{10}\$.*$')
    reRomReference = re.compile('^ROM-Reference:$')
    reAddress = re.compile('^\s+\$[0-9A-F]{2,4}\/[0-9]{1,5}\:\s+.*$')
    reAddressRange = re.compile('^\s+\$[0-9A-F]{2,4}\-\$[0-9A-F]{2,4}\/[0-9]{1,5}\-[0-9]{1,5}\:\s+.*$')
    reAddressBlock = re.compile('^\s+\$[0-9A-F]{2,4}\+\$[0-9A-F]{2,4}\/[0-9]{1,5}\+[0-9]{1,5}\:\s+.*$')
    reAddressVia = re.compile('^\s+\$[0-9A-F]{2,4}\/[0-9]{1,5}\/VIA[12]\+[0-9]{1,2}\:\s+.*$')
    reAsm = re.compile('^\s[A-Z]{3}\s(\$|\().*$')
    reAsmAddressBlock = re.compile('^\s{14}(\$[0-9A-F]{4}\s?)+$')
    reInfoText = re.compile('^\s(\s{2})?[a-zA-Z0-9\-\/\$\;\:\.\,\(\)/#]+(\s{1,2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+)*$')
    reBodyText = re.compile('^\s{2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+(\s{1,2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+)*$')
    reEmptyLine = re.compile('^$')

    for line in data.split('\n'):
        if reError.match(line):
            # Error ¤123: abc
            pass
        elif reTableBreak.match(line):
            # +----+----+----+
            pass
        elif reTableRow.match(line):
            # | ab | cd | ef |
            pass
        elif reHeadingBreak.match(line):
            # +---------------
            pass
        elif reHeadingRow.match(line):
            # | abc
            pass
        elif reMemoryLine.match(line):
            # 12AF: ...
            pass
        elif reJumpFrom.match(line):
            # Jump from: $1234...
            pass
        elif reJumpFromNext.match(line):
            #            $1234...
            # TODO only directly after reJumpFrom
            pass
        elif reRomReference.match(line):
            # ROM-Reference:
            pass
        elif reAddress.match(line):
            #  $1234/65432: abc
            pass
        elif reAddressRange.match(line):
            #  $1234-$2345/456-567: abc
            pass
        elif reAddressBlock.match(line):
            #  $1234+$2345/345+456: abc
            pass
        elif reAddressVia.match(line):
            #  $1234/2345/VIA1+3: abc
            pass
        elif reAsm.match(line):
            # LDA $...
            pass
        elif reAsmAddressBlock.match(line):
            #             $1234 $2345...
            pass
        elif reInfoText.match(line):
            #    This is link body text, but with 3 spaces indent...
            pass
        elif reBodyText.match(line):
            #   This is a (piece) of, text, with #1 numbers...
            pass
        elif reEmptyLine.match(line):
            # <empty line>
            # TODO take action based on previous line
            pass
        else:
            print(line)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        chm_html_to_md('html/aay1541/aay1541.htm')
    elif len(sys.argv) == 2:
        chm_html_to_md(sys.argv[1])
    else:
        print("usage hacking.py <filename>")


