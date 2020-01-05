# applied-tm-course
Github Repository supporting the Applied TM Course as part of the VU Text Mining Masters

This repository contains code and materials that provide additional support for the Applied Text Mining course.

The directory example_scripts/ contains:


/extract_information_from_naf.py

What is it? 
This script illustrates how to extract entities and opinions from a NAF file using the KafNafParserPy module.
It takes a directory of naf files as input and produces a csv files in an (existing) specified output directory. These csv files provide an overview of the entities or the opinions that are provided in the naf file.


How can I install the dependencies (the KafNafParserPy module):

The KafNafParserPy module can be installed using pip:
pip install KafNafParserPy

How to run the script?
The script can be run from the commandline:

python extract_information_from_naf.py inputdir/ outputdir/ \[-o -e\]

inputdir/ : path to the directory with naffiles (obligatory argument)
outputdir/ : path to the directory where the output csv files should be generated (obligatory argument)
-o : option that requests extraction of opinions
-e : option the requests extraction of expressions
NB: both options can be specified at the same time: the script will then generate both opinions and entities csv files.

For more information run:

python extract_information_from_naf.py --help
