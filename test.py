from solidity_parser import parser
import sys
import pprint
ast = parser.parse_file(sys.argv[1])
objectified_source_unit = parser.objectify(ast)
pprint.pprint(ast)