import re
import sys
import textwrap

# Map of regular expressions used
remap = {
    'error': re.compile('^\s+Error \#\d+:.*$'),
    'table_break': re.compile('^\s*\+[+-]+\+$'),
    'table_row': re.compile('^\s*\|.+\|$'),
    'toc_break': re.compile('^\s+\+\-+$'),
    'toc_row': re.compile('^\s+\|.*$'),
    'memory_line': re.compile('^[0-9A-F]{4}:\s+.*$'),
    'jump': re.compile('^Jump from \$.*$'),
    'jump_next': re.compile('^\s{10}\$.*$'),
    'rom_reference': re.compile('^ROM-Reference:$'),
    'address': re.compile('^\s+\$[0-9A-F]{2,4}\/[0-9]{1,5}\:\s+.*$'),
    'address_range': re.compile('^\s+\$[0-9A-F]{2,4}\-\$[0-9A-F]{2,4}\/[0-9]{1,5}\-[0-9]{1,5}\:\s+.*$'),
    'address_block': re.compile('^\s+\$[0-9A-F]{2,4}\+\$[0-9A-F]{2,4}\/[0-9]{1,5}\+[0-9]{1,5}\:\s+.*$'),
    'address_via': re.compile('^\s+\$[0-9A-F]{2,4}\/[0-9]{1,5}\/VIA[12]\+[0-9]{1,2}\:\s+.*$'),
    'asm': re.compile('^\s[A-Z]{3}\s(\$|\().*$'),
    'asm_address_block': re.compile('^\s{14}(\$[0-9A-F]{4}\s?)+$'),
    'info_text': re.compile('^\s(\s{2})?[a-zA-Z0-9\-\/\$\;\:\.\,\(\)/#]+(\s{1,2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+)*$'),
    'body_text': re.compile('^\s{2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+(\s{1,2}[a-zA-Z0-9\>\=\-\/\$\;\:\.\,\(\)\#]+)*$'),
    'empty_line': re.compile('^$'),
}

def chm_html_to_md(filename):
    with open(filename, 'r') as f:
        data = f.read()

    lines = parse_html(data)
    lines = simplify_lines(lines)
    print(output_markdown(lines))

def parse_html(data):
    """
        Takes the contents of a file, splits it into lines and maps each line 
        to a regular expression from remap.
    """
    res = []
    for line in data.split('\n'):
        for rek in remap:
            if remap[rek].match(line):
                res.append((rek, line))
                break
        else:
            res.append(('unidentified', line))
            
    return res

def output_markdown(lines):
    res = []
    
    last_line_type = None
    for line in lines:
        # Insert a blank line after the following types of blocks:
        if last_line_type != line[0]:
            if last_line_type in ['memory_line', 'jump', 'rom_reference', 'asm']:
                res.append('')

        if line[0] == 'error':
            res.append("### " + line[1]) # TODO
            res.append('')
        elif line[0] == 'table_row':
            if last_line_type == 'table_row':
                res.append(line[1])
            else:
                pass # Skip first row, it is empty
        elif line[0] == 'table_end':
            res.append('')
        elif line[0] == 'toc_title':
            res.append('## ' + line[1] + '\n')
        elif line[0] == 'toc_row':
            res.append('    ' + line[1])
        elif line[0] == 'toc_end':
            res.append('')
        elif line[0] == 'toc_end':
            res.append('') # TODO
        elif line[0] == 'memory_line':
            res.append(line[1]) # TODO
        elif line[0] == 'jump':
            res.append(line[1])
        elif line[0] == 'rom_reference':
            res.append(line[1]) # TODO
        elif line[0] == 'address':
            res.append('\n\n### ' + line[1])
            res.append('')
        elif line[0] == 'asm':
            res.append('    ' + line[1])
        elif line[0] == 'info_text':
            for l in textwrap.wrap(line[1], width=72):
                res.append('    ' + l)
            res.append('')
        elif line[0] == 'body_text':
            for l in textwrap.wrap(line[1], width=80):
                res.append(l)
            res.append('')
        elif line[0] == 'unidentified':
            res.append('>>>>>> UNIDENTIFIED')
            res.append(line[1])
            res.append('<<<<<<')
        else:
            raise Exception('Unknown line type "%s"' % (line[0]))
        
        last_line_type = line[0]
        
    return "\n".join(res)

def table_split(text):
    """
        Helper to split a table row into a list of stripped strings
    """
    t = text.strip()
    assert t[0] == '|'
    assert t[-1] == '|'
    t = t[1:-1]
    texts = []
    for t2 in t.split('|'):
        texts.append(t2.strip())
    return texts

def table_join(texts):
    """
        Helper to join table strings into a table row
    """
    return '|' + '|'.join(texts) + '|'

def simplify_lines(lines):
    """
        Performs the following transformations on the given lines:
        
        - Transform table_break and table_row into table_row lines ended by a table_end
        - Transform toc_break and toc_row into toc_title and toc_row lines ended by a toc_end
        - Merges any jump_next following a jump line
        - Merge address, address_block, address_range, and address_via into address
        - Merges any asm_address_block following an asm line
        - Merges consecutive body_text lines
        - Strips out any empty lines
    """
    res = []
    
    toc_start_index = -1
    toc_has_title = False
    last_line = (None, None)
    for line in lines:
        if len(res) > 0:
            # Close tables and headings
            if res[-1][0] == 'table_row' and line[0] not in ['table_row', 'table_break']:
                res.append(('table_end', None))
            elif res[-1][0] == 'toc_row' and line[0] not in ['toc_row', 'toc_break']:
                toc_start_index = -1
                toc_has_title = False
                res.append(('toc_end', None))
        
        if line[0] == 'error':
            res.append((line[0], line[1].strip())) # TODO
        elif line[0] == 'table_break':
            # If this is the first line of table, initiate an empty row, otherwise, skip
            if res[-1][0] != 'table_row':
                text = line[1]
                text = text.replace(' ', '')
                text = text.replace('-', '')
                text = text.replace('+', '|')
                res.append(('table_row', text))
        elif line[0] == 'table_row':
            # Merge consecutive table_rows if there is at least one empty column, 
            # otherwise add a new one (e.g. after a table_break)
            if last_line[0] == 'table_row' and res[-1][0] == 'table_row':
                rts = table_split(res[-1][1])
                lts = table_split(line[1])
                assert len(lts) == len(rts)
                ts = []
                has_zero = False
                for ii in range(len(lts)):
                    ts.append(' '.join([rts[ii], lts[ii]]))
                    if len(lts[ii]) == 0:
                        has_zero = True
                if has_zero:
                    res[-1] = (res[-1][0], table_join(ts))
                else:
                    res.append((line[0], table_join(lts)))
            else:
                ts = table_split(line[1])
                res.append((line[0], table_join(ts)))
        elif line[0] == 'toc_break':
            text = line[1].strip()
            res.append(('toc_row', text))
            if toc_start_index == -1:
                toc_has_title = False
                toc_start_index = len(res)-1
        elif line[0] == 'toc_row':
            text = line[1].strip()
            res.append(('toc_row', text))
            if not toc_has_title and text != '|':
                toc_has_title = True
                text = text[1:].strip()
                res.insert(toc_start_index, ('toc_title', text))
        elif line[0] == 'memory_line':
            res.append(line) # TODO
        elif line[0] == 'jump':
            # Append as is
            res.append(line)
        elif line[0] == 'jump_next':
            # Strip and merge with prior 'jump'
            if last_line[0] in ['jump', 'jump_next'] and res[-1][0] != 'jump':
                raise Exception('Orphaned "just_next" encountered')
            
            res[-1] = (res[-1][0], ' '.join([res[-1][1], line[1].strip()]))
        elif line[0] == 'rom_reference':
            # Append as is
            res.append(line)
        elif line[0] in ['address', 'address_range', 'address_block', 'address_via']:
            res.append(('address', line[1]))
        elif line[0] == 'asm':
            # Strip spaces from left
            res.append((line[0], line[1].lstrip()))
        elif line[0] == 'asm_address_block':
            # Strip and merge with prior 'asm'
            if last_line in ['asm', 'asm_address_block'] and res[-1][0] != 'asm':
                raise Exception('Orphaned "asm_address_block" encountered')
            
            res[-1] = (res[-1][0], ' '.join([res[-1][1], line[1].strip()]))
        elif line[0] == 'info_text':
            # Strip lines, merge consecutive lines
            text = line[1].strip()
            if last_line[0] == 'info_text':
                res[-1] = (line[0], ' '.join([res[-1][1], text]))
            else:
                res.append((line[0], text))
        elif line[0] == 'body_text':
            # Strip lines, merge consecutive lines
            text = line[1].strip()
            if last_line[0] == 'body_text':
                res[-1] = (line[0], ' '.join([res[-1][1], text]))
            else:
                res.append((line[0], text))
        elif line[0] == 'empty_line':
            pass
        elif line[0] == 'unidentified':
            # Merge with preserved line-breaks
            if last_line[0] == 'unidentified':
                res[-1] = (res[-1][0], '\n'.join([res[-1][1], line[1]]))
            else:
                res.append(line)
        else:
            raise Exception('Unknown line type "%s"' % (line[0]))
        
        last_line = line

    return res

if __name__ == '__main__':
    if len(sys.argv) == 1:
        chm_html_to_md('html/aay1541/aay1541.htm')
    elif len(sys.argv) == 2:
        chm_html_to_md(sys.argv[1])
    else:
        print("usage hacking.py <filename>")


