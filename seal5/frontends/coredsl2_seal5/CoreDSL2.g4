// SPDX-License-Identifier: Apache-2.0

/*
 * This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
 *
 * Copyright (C) 2022
 * Chair of Electrical Design Automation
 * Technical University of Munich
 */

grammar CoreDSL2;

description_content
	: imports+=import_file* definitions+=isa+
	;

import_file
	: 'import' uri=STRING
	;

isa
	: 'InstructionSet' name=IDENTIFIER ('extends' extension+=IDENTIFIER (',' extension+=IDENTIFIER)*)? '{' sections+=section+ '}' # instruction_set
	| 'Core' name=IDENTIFIER ('provides' contributing_types+=IDENTIFIER (',' contributing_types+=IDENTIFIER)*)? '{' sections+=section* '}' # core_def
	;

section
	: type_='architectural_state' '{' (declarations+=declaration | expressions+=expression ';')+ '}' # section_arch_state
	| type_='functions' '{' functions+=function_definition* '}' # section_functions
	| type_='instructions' attributes+=attribute* '{' instructions+=instruction+ '}' # section_instructions
	| type_='always' attributes+=attribute* '{' always_blocks+=always_block+ '}' # section_always
	;

always_block
	: name=IDENTIFIER attributes+=attribute* behavior=block;

instruction
	: name=IDENTIFIER attributes+=attribute* '{'
	'encoding' ':' encoding+=encoding_entry ('::' encoding+=encoding_entry)*';'
	('assembly' ':' (assembly=STRING | '{' mnemonic=STRING ',' assembly=STRING '}') ';')?
	'behavior' ':' behavior=statement
	'}'
	;

rule_encoding
	: fields+=encoding_entry ('::' fields+=encoding_entry)*
	;

encoding_entry
	: value=integer_constant # bit_value
	| name=IDENTIFIER '[' left=integer_constant ':' right=integer_constant ']' # bit_field
	;

function_definition
	: extern='extern' type_=type_specifier name=IDENTIFIER '(' params=parameter_list? ')' attributes+=attribute* ';'
	| type_=type_specifier name=IDENTIFIER '(' params=parameter_list? ')' attributes+=attribute* (behavior=block | ';')
	;

parameter_list
	: params+=parameter_declaration (',' params+=parameter_declaration)*
	;

parameter_declaration
	: type_=type_specifier decl=declarator?
	;

statement
	: block # block_statement
	| ref=IDENTIFIER '(' (args+=expression (',' args+=expression)*)? ')' ';' # procedure_call
	| type_='if' '(' cond+=expression ')' stmt+=statement ('else' 'if' '(' cond+=expression ')' stmt+=statement)* ('else' stmt+=statement)? # if_statement
	| type_='for' '(' cond=for_condition ')' stmt=statement # for_statement
	| type_='while' '(' cond=expression ')' stmt=statement # while_statement
	| type_='do' stmt=statement 'while' '(' cond=expression ')' ';' # do_statement
	| type_='switch' '(' cond=expression ')' '{' items+=switch_block_statement_group* switch_label* '}' # switch_statement
	| type_='return' expr=expression? ';' # return_statement
	| type_='break' ';' # break_statement
	| type_='continue' ';' # continue_statement
	| type_='spawn' stmt=statement # spawn_statement
	| expr=expression ';' # expression_statement
	;

switch_block_statement_group
	: labels+=switch_label+ statements+=statement+
	;

switch_label
	: 'case' const_expr=expression ':'
	| 'default' ':'
	;

block
	: '{' items+=block_item* '}'
	;

block_item
	: statement
	| declaration
	;

for_condition
	: (start_decl=declaration | start_expr=expression? ';')
	  end_expr=expression? ';'
	  (loop_exprs+=expression (',' loop_exprs+=expression)*)?
	;

declaration
	: (storage+=storage_class_specifier | qualifiers+=type_qualifier | attributes+=attribute)*
		type_=type_specifier
		(declarations+=declarator (',' declarations+=declarator)*)? ';'
	;

type_specifier
	: type_=value_type_specifier (ptr='*' | ptr='&')?
	;

value_type_specifier
	: signed=integer_signedness (shorthand=integer_shorthand | '<' size=primary '>') # integer_type
	| shorthand=integer_shorthand # integer_type
	| shorthand=float_shorthand # float_type
	| type_='bool' # bool_type
	| type_='void' # void_type
	| type_=struct_or_union name=IDENTIFIER? '{' declarations+=struct_declaration* '}' # composite_declaration
	| type_=struct_or_union name=IDENTIFIER # composite_reference
	| type_='enum' name=IDENTIFIER? '{' enumerator_list ','? '}' # enum_declaration
	| type_='enum' name=IDENTIFIER # enum_reference
	;

integer_signedness
	: 'unsigned'
	| 'signed'
	;

integer_shorthand
	: 'char'
	| 'short'
	| 'int'
	| 'long'
	;

float_shorthand
	: 'float'
	| 'double'
	;

attribute
	: '[[' name=IDENTIFIER ('=' params+=expression | '(' params+=expression (',' params+=expression)* ')')? ']]'
	;

bit_size_specifier
	: '<' size+=primary (',' size+=primary ',' size+=primary ',' size+=primary)? '>'
	;

enumerator_list
	: enumerators+=enumerator (',' enumerators+=enumerator)*
	;

enumerator
	: name=IDENTIFIER
	| name=IDENTIFIER '=' expression
	;

struct_declaration
	: specifier=struct_declaration_specifier declarators+=declarator(',' declarators+=declarator)* ';'
	;

struct_declaration_specifier
	: type_=type_specifier
	| qualifiers+=type_qualifier
	;

declarator
	: name=IDENTIFIER
		(LEFT_BR size+=expression RIGHT_BR)*
		attributes+=attribute*
		('=' init=initializer)?
	;

initializer
	: expr=expression
	| '{' initializerList ','? '}'
	;

initializerList
	: (designated_initializer | initializer) (',' (designated_initializer | initializer))*
	;

designated_initializer
	: designators+=designator+ '=' init=initializer
	;

designator
	: LEFT_BR idx=expression RIGHT_BR
	| '.' prop=IDENTIFIER
	;

expression
	: primary # primary_expression
	| bop=('.' | '->') ref=IDENTIFIER # deref_expression
	| expr=expression bop='[' left=expression (':' right=expression)? ']' # slice_expression
	| ref=IDENTIFIER '(' (args+=expression (',' args+=expression)*)? ')' # method_call
	| left=expression op=('++' | '--') # postinc_expression
	| op=('++'|'--') right=expression # preinc_expression
	| prefix=('&'|'*'|'+'|'-') right=expression # prefix_expression
	| prefix=('~'|'!') right=expression # prefix_expression
	| '(' (type_=type_specifier | sign=integer_signedness) ')' right=expression # cast_expression
	| left=expression bop=('*'|'/'|'%') right=expression # binary_expression
	| left=expression bop=('+'|'-') right=expression # binary_expression
	| left=expression bop=('<<' | '>>') right=expression # binary_expression
	| left=expression bop=('<=' | '>=' | '>' | '<') right=expression # binary_expression
	| left=expression bop=('==' | '!=') right=expression # binary_expression
	| left=expression bop='&' right=expression # binary_expression
	| left=expression bop='^' right=expression # binary_expression
	| left=expression bop='|' right=expression # binary_expression
	| left=expression bop='&&' right=expression # binary_expression
	| left=expression bop='||' right=expression # binary_expression
	| left=expression bop='::' right=expression # concat_expression
	| <assoc=right> cond=expression bop='?' then_expr=expression ':' else_expr=expression # conditional_expression
	| <assoc=right> left=expression bop=('=' | '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '^=' | '>>=' | '>>>=' | '<<=' | '%=') right=expression # assignment_expression
	;

primary
	: ref=IDENTIFIER # reference_expression
	| const_expr=constant # constant_expression
	| literal+=string_literal+ # literal_expression
	| '(' expr=expression ')' # parens_expression
	;

string_literal
	: ENCSTRINGCONST
	| STRING
	;

constant
	: integer_constant
	| floating_constant
	| character_constant
	| string_constant
	| bool_constant
	;

integer_constant
	: value=INTEGER
	;

floating_constant
	: value=FLOAT
	;

bool_constant
	: value=BOOLEAN
	;

character_constant
	: value=CHARCONST
	;

string_constant
	: value=STRING
	;

double_left_bracket
	: LEFT_BR LEFT_BR
	;

double_right_bracket
	: RIGHT_BR RIGHT_BR
	;

data_types
	: 'bool'
	| 'char'
	| 'short'
	| 'int'
	| 'long'
	| 'signed'
	| 'unsigned'
	| 'float'
	| 'double'
	| 'void'
	| 'alias'
	;

type_qualifier
	: 'const'
	| 'volatile'
	;

storage_class_specifier
	: 'extern'
	| 'static'
	| 'register'
	;

struct_or_union
	: 'struct'
	| 'union'
	;

LEFT_BR: '[';
RIGHT_BR: ']';

BOOLEAN: ('true'|'false');
FLOAT: ('0'..'9')+ '.' ('0'..'9')* (('e'|'E') ('+'|'-')? ('0'..'9')+)? ('f'|'F'|'l'|'L')?;
INTEGER: (BINARYINT|HEXADECIMALINT|OCTALINT|DECIMALINT|VLOGINT) ('u'|'U')? (('l'|'L') ('l'|'L')?)?;

fragment BINARYINT: ('0b'|'0B') '0'..'1' ('_'? '0'..'1')*;
fragment OCTALINT: '0' '_'? '0'..'7' ('_'? '0'..'7')*;
fragment DECIMALINT: ('0'|'1'..'9' ('_'? '0'..'9')*);
fragment HEXADECIMALINT: ('0x'|'0X') ('0'..'9'|'a'..'f'|'A'..'F') ('_'? ('0'..'9'|'a'..'f'|'A'..'F'))*;
fragment VLOGINT: ('0'..'9')+ '\'' ('s')? ('b' ('0'..'1')+|'o' ('0'..'7')+|'d' ('0'..'9')+|'h' ('0'..'9'|'a'..'f'|'A'..'F')+);

IDENTIFIER: '^'? ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;

CHARCONST: ('u'|'U'|'L')? '\'' ('\\' .|~('\\'|'\''))* '\'';
ENCSTRINGCONST: ('u8'|'u'|'U'|'L') '"' ('\\' .|~('\\'|'"'))* '"';
STRING: ('"' ('\\' .|~('\\'|'"'))* '"'|'\'' ('\\' .|~('\\'|'\''))* '\'');

ML_COMMENT: '/*' .*?'*/' -> skip;
SL_COMMENT: '//' ~('\n'|'\r')* ('\r'? '\n')? -> skip;
WS: (' '|'\t'|'\r'|'\n')+ -> skip;
