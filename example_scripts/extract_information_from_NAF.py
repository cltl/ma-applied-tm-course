from KafNafParserPy import *

### KafNafParserPy: https://github.com/cltl/KafNafParserPy

import argparse
import os
import csv



def get_tokens_from_term_span(nafobj,span):
    '''
    Retrieves tokens based on a list of term ids and returns string made up of tokens
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file
    @type span: list of strings
    @param span: the term ids that make up a span
    @rtype: string
    @return: the string of tokens that makes up the span
    '''
    tokens = ''
    for term_id in span:
        term = nafobj.get_term(term_id)
        term_span = term.get_span().get_span_ids()
        for token_id in term_span:
            token = nafobj.get_token(token_id)
            tokens += token.get_text() + ' '
    return tokens.strip()


def extract_entities(nafobj):
    '''
    Function that extracts all entities from a naf file and returns relevant information as list of dictionaries
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file
    @rtype: list of dict
    @returns: a list of dictionaries that provide relevant information for each entity in the NAF file
    '''
    rows = []
    for entity in nafobj.get_entities():
        references = []
        for reference in entity.get_references():
            term_ids = reference.get_span().get_span_ids()
            tokens = get_tokens_from_term_span(nafobj, term_ids)
            references.append([term_ids, tokens])
        for reference in references:
            row = {}
            row['id'] = entity.get_id()
            row['type'] = entity.get_type()
            row['term_ids'] = ",".join(reference[0])
            row['surface_string'] = reference[1]
        rows.append(row)
    return rows


def extract_opinions(nafobj):
    '''
    Function that extracts opinions from a naf file and returns relevant information as list of dictionaries
    @type nafobj: KafNafParser
    @param nafobj: NAF object for file
    @rtype: list of dict
    @returns: a list of dictionaries that provide relevant information for each opinion in the NAF file
    '''
    rows = []
    for opinion in nafobj.get_opinions():
        row = {}
        row['id'] = opinion.get_id()
        if opinion.get_expression() is not None:
            expression = opinion.get_expression()
            row['polarity'] = expression.get_polarity()
            row['strength'] = expression.get_strength()
            span_term_ids = expression.get_span().get_span_ids()
            row['e_term_ids'] = ",".join(span_term_ids)
            row['expression'] = get_tokens_from_term_span(nafobj,span_term_ids)
        else:
            for keyname in ['polarity','strength','e_terms_ids','expression']:
                row[keyname] = '-'
        if opinion.get_holder() is not None:
            span_term_ids = opinion.get_holder().get_span().get_span_ids()
            row['h_term_ids'] = ",".join(span_term_ids)
            row['holder'] = get_tokens_from_term_span(nafobj,span_term_ids)
        else:
            row['h_term_ids'] = '-'
            row['holder'] = '-'
        if opinion.get_target() is not None:
            span_term_ids = opinion.get_target().get_span().get_span_ids()
            row['t_term_ids'] = ",".join(span_term_ids)
            row['target'] = get_tokens_from_term_span(nafobj,span_term_ids)
        else:
            row['t_term_ids'] = '-'
            row['target'] = '-'
        rows.append(row)
    return rows

def generate_output(outputfile, rows):
    '''
    Creates a csvfile from list of dictionaries and writes it out to an outputfile
    @type outputfile: string
    @param outputfile: name of the outputfile
    @type rows: list of dict
    '''
    #https://docs.python.org/3/library/csv.html
    with open(outputfile, 'w') as csvfile:
        fieldnames = list(rows[0].keys())
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for row in rows:
            csvwriter.writerow(row)

def extract_information(my_arguments):
    '''
    Calls relevant functions for extracting specified information and generating output csv files
    @type my_arguments: Namespace object
    @param my_arguments: arguments passed through the commandline
    '''
    
    naf_directory = my_arguments.inputdir[0]
    output_directory = my_arguments.outputdir[0]
    for naffile in os.listdir(naf_directory):
        filename = naffile.rstrip('.naf')
        nafobj = KafNafParser(naf_directory + '/' + naffile)
        if my_arguments.entities:
            entity_info = extract_entities(nafobj)
            if len(entity_info) > 0:
                generate_output(output_directory + '/' + filename + '-entities.csv', entity_info)
        if my_arguments.opinions:
            opinion_info = extract_opinions(nafobj)
            if len(opinion_info) > 0:
                generate_output(output_directory+ '/' + filename + '-opinions.csv', opinion_info)

def define_commandline_input():
    '''
    Defines arguments. options and commands for the commandline (using the argparse package)
    @rtype: ArgumentParser
    @returns: parser with all commandline arguments, options and commands
    '''
    
    #https://docs.python.org/3/library/argparse.html

    parser = argparse.ArgumentParser(description='extracts information from NAF files')
    #adding obligatory arguments of input file and output file
    parser.add_argument('inputdir', metavar='in', type=str, nargs=1, help='path to the directory of input dirs (NAF)')
    parser.add_argument('outputdir', metavar='out', type=str, nargs=1, help='path to directory of outputdirs (CSV)')
    #optional arguments of what you would like to extract
    parser.add_argument('-e', '--entities', action='store_true', help='extract entity information')
    parser.add_argument('-o', '--opinions', action='store_true', help='extract opinion information')
    
    return parser

def main():
    '''
    Creates commandline argument parser and reads in arguments from the commandline
    Calls extraction function if at least one type of information is requested
    '''
    
    parser = define_commandline_input()
    my_arguments = parser.parse_args()
    
    #only looping through files if information is indeed requested.
    #make sure to update the if-statement once new options are added.
    if my_arguments.entities or my_arguments.opinions:
        extract_information(my_arguments)
    else:
        print('No information requested. See help for options')

if __name__ == '__main__':
    main()
