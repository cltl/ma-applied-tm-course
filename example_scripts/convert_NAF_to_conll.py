from KafNafParserPy import *

### KafNafParserPy: https://github.com/cltl/KafNafParserPy

import argparse
import os
import csv



def get_token_information(nafobj,term_span):
    '''
    Retrieves a token_obj from a term_span (length 1) and returns and offset, sentence number and token
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file
    @type span: list of strings
    @param span: the term ids that make up a span
    @rtype: string, string, int
    @return: the token, sentence number and offset
    '''
    if len(term_span) == 1:
        token = nafobj.get_token(term_span[0])
        text = token.get_text()
        sentence = token.get_sent()
        #set offset to int for comparison
        offset = int(token.get_offset())
        return text, sentence, offset
    else:
        print('WARNING: NAF file contains multiwords or terms without spans: code needs to be adapted to deal with this')



def collect_entity_information(nafobj, conll_rows):
    '''
    Function that extracts all entities from a naf file and adds relevant information to the conll dictionary
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file
    @type conll_rows: dict
    @param conll_rows: the information collected for conll file so far
    '''
    for entity in nafobj.get_entities():
        etype = entity.get_type()
        for reference in entity.get_references():
            first = True
            for term_id in reference.get_span().get_span_ids():
                key_id = term_id.lstrip('t')
                if first:
                    conll_rows[key_id]['nerc'] = 'B-' + etype
                    first = False
                else:
                    conll_rows[key_id]['nerc'] = 'I-' + etype
    #add value 'O' to all non-entities
    for row in conll_rows:
        if not 'nerc' in conll_rows[row]:
            conll_rows[row]['nerc'] = 'O'


def create_basic_information_dictionary(nafobj, my_arguments):
    '''
    Creates a dictionary with term_id based keys that takes a dictionary with conll rows as values.
    This function picks up basic information from term and token layer
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file that is converted
    @type my_arguments: Namespace object
    @param my_arguments: arguments passed through the commandline
    @rtype: dict
    @returns: a dictionary with term_id based keys and a conll row value dictionary as value
    '''
    conll_rows = {}
    offset = -1
    for term in nafobj.get_terms():
        term_span = term.get_span().get_span_ids()
        token, sentence_nr, tok_offset = get_token_information(nafobj, term_span)
        if tok_offset < offset:
            print('WARNING: terms in NAF file are not ordered according to surface order of raw text. Adapt code to deal with this')
        else:
            #using numbers as identifiers
            key_id = term.get_id().lstrip('t')
            #basis information:
            row = {'id': key_id, 'sent_id': sentence_nr, 'token': token}
            if my_arguments.lemmas:
                row['lemma'] = term.get_lemma()
            if my_arguments.pos:
                row['pos'] = term.get_pos()
            if my_arguments.morph:
                row['morph'] = term.get_morphofeat()
            #Python by default outputs key-value pairs in the order they were placed in (nowadays)
            #for older versions of Python: store identifiers as integers (so you can later loop through sorted keys)
            conll_rows[key_id] = row
    return conll_rows

def generate_output(outputfile, rows):
    '''
        Creates a csvfile from list of dictionaries and writes it out to an outputfile
        @type outputfile: string
        @param outputfile: name of the outputfile
        @type rows: list of dict
        '''
    #https://docs.python.org/3/library/csv.html
    with open(outputfile, 'w') as csvfile:
        set_up = False
        #loop through values
        for row in rows.values():
            if not set_up:
                fieldnames = list(row.keys())
                csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter='\t')
                csvwriter.writeheader()
                set_up = True
            csvwriter.writerow(row)

def convert_naf_files_to_conll(my_arguments):
    '''
    Calls relevant functions for extracting specified information and generating output conll files
    @type my_arguments: Namespace object
    @param my_arguments: arguments passed through the commandline
    '''
    
    naf_directory = my_arguments.inputdir[0]
    output_directory = my_arguments.outputdir[0]
    for naffile in os.listdir(naf_directory):
        filename = naffile.rstrip('.naf') + '.conll'
        nafobj = KafNafParser(naf_directory + '/' + naffile)
        #terms are the main elements connecting layers in NAF. We also start from there.
        conll_rows = create_basic_information_dictionary(nafobj, my_arguments)
        if my_arguments.entities:
            collect_entity_information(nafobj, conll_rows)
        generate_output(output_directory + '/' + filename, conll_rows)

def define_commandline_input():
    '''
    Defines arguments. options and commands for the commandline (using the argparse package)
    @rtype: ArgumentParser
    @returns: parser with all commandline arguments, options and commands
    '''
    
    #https://docs.python.org/3/library/argparse.html

    parser = argparse.ArgumentParser(description='converts NAF files to conll representations')
    #adding obligatory arguments of input file and output file
    parser.add_argument('inputdir', metavar='in', type=str, nargs=1, help='path to the directory of input dirs (NAF)')
    parser.add_argument('outputdir', metavar='out', type=str, nargs=1, help='path to directory of outputdirs (conll)')
    #optional arguments of what you would like to extract
    parser.add_argument('-e', '--entities', action='store_true', help='include entity information')
    parser.add_argument('-p', '--pos', action='store_true', help='include pos-tags')
    parser.add_argument('-l', '--lemmas', action='store_true', help='include lemmas')
    parser.add_argument('-m', '--morph', action='store_true', help='include lemmas')
    
    
    return parser

def main():
    '''
    Creates commandline argument parser and reads in arguments from the commandline
    Calls extraction function if at least one type of information is requested
    '''
    
    parser = define_commandline_input()
    my_arguments = parser.parse_args()

    convert_naf_files_to_conll(my_arguments)


if __name__ == '__main__':
    main()
