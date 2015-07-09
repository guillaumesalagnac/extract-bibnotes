#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import sys
import subprocess
import argparse

def trim(string):
    """Remove garbage around field name"""
    return string.strip(" \n\t,=")

def find_field(string):
    string=string.strip()
    if string[0] == '{':
        nesting=0
        boundary=0
        while True:
            # look for parentheses
            if string[boundary] == '{': nesting+=1
            if string[boundary] == '}': nesting-=1
            # advcance to next char
            boundary += 1
            # if we are back to zero then we're done
            if  nesting == 0:
                return [ string[:boundary][1:-1] , # 1:-1 to skip braces
                         string[boundary:] ]
    else:
        return re.split('([a-zA-Z_0-9]+)',string,1)[1:]

def parseentry( data ):
    entry={}
    if data[0] != '@':
        raise Exception

    [entrytype,data] = data.split('{',1)
    entry['type'] = entrytype[1:].lower()

    [key,data] = data.split(',',1)
    entry['key'] = trim(key)

    while '=' in data:
        # print 70*"=" +"\n"+ data + "\n" + 30*"="
        [fieldname, data] = data.split('=',1)
        fieldname=trim(fieldname).lower()
        # print '<'+fieldname+'>'
        [contents, data] = find_field(data)
        # print '<<'+contents+'>>'
        entry[fieldname] = contents

    return entry


def parsebibdata( text ):
    entries={}
    strings=text.split('@')
    for string in strings:
        # (simplistic) sanity  check to avoid plenty  of exceptions in
        # by jabref file (which has both styles of bibtex comments)
        if "Title" not in string and "Author" not in string:
            # print "this is not a bibtex entry:",string
            continue
        try:
            entry = parseentry('@'+string)
            entries[entry['key']]=entry
        except:
            print "could not parse bibtex entry:"
            print string
    return entries

if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description="extract biblatex-friendly 'annotation' fields from bibtex entries")
    argparser.add_argument("bibfile",metavar="BIBFILE",help="your .bib file")
    argparser.add_argument("keys",metavar="KEY",nargs='*',help="bibtexkey(s) to be extracted")
    
    options=argparser.parse_args()

    entries=parsebibdata( open(options.bibfile).read() )

    # print "entries:",entries.keys()

    # if the user  specified particular keys to be  extracted, then we
    # make sure these actually exist
    for key in options.keys:
        if key not in entries:
            print "could not find bibtex entry %s in %s" % (key,options.bibfile)
            sys.exit(1)

    # if the user  specified particular keys to be  extracted, then we
    # only look at these
    for key in entries.keys():
        if len(options.keys) and key not in options.keys:
            del entries[key]

    for key in entries.keys():
        entry = entries[ key ]
        if 'annotation' in entry:
            del entries[ key ] # we remove successfuly processed entries

            mdfile = 'bibannotation-%s.md' % key
            texfile = 'bibannotation-%s.tex' % key
            with open( mdfile , 'w' ) as f:
                print "extracting "+f.name
                text=entry[ 'annotation' ]
                ## fix some plain-text-to-latex issues
                text=text.replace('μ','\ensuremath{\mu}')
                text=text.replace('α','\ensuremath{\alpha}')
                ## mimic syntatic sugar from txt2pdf
                # automagically detect bullet lists, even without preceding blank line
                text=re.sub(':\n- ',':\n\n- ',text)
                # turn my two-spaces nested lists into four-spaces markdown lists
                text="\n".join([ re.sub('^ - ', '    - ', line) for line in text.split("\n")])
                # turn empty lines into biskips to space out text a bit
                text=re.sub('\n\n','\n\n\\\\bigskip\n\n',text)
                f.write(text)
                
            
            subprocess.call("pandoc -f markdown -t latex %s > %s" % (mdfile,texfile), shell=True )

    # if some entries have not been removed, it means they were not processed successfuly
    if len( entries.keys() ):
        print "could not find annotations for entries:"," ".join(entries.keys())
