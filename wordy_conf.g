grammar wordy_conf;

pipeline: DECL_PIP_STRAT stratName=STRING dataset_path  exp_folder  data_dump?  with_dec_depth with_splcies
          par_exp_name  log output ignores? conf? child+;

DECL_PIP_STRAT: 'declare pipeline strategy:';
dataset_path: 'with dataset path:' STRING;
exp_folder: 'with experiment folder:' STRING;
data_dump: 'generate data';
with_dec_depth: 'with decision tree depth:' int_list;
with_splcies: 'splits:' DIGIT;


par_exp_name: 'set parent experiment name:' STRING;
log         : 'with log:' STRING;
output      : 'with output folder:' STRING;
ignores     : 'with auto-ignores:' string_list;
conf        : 'with configuration:' STRING;

child: name=STRING 'is' (model | procedural | payload);

payload: payload_type 'attribute' attrn=STRING 'as' (STRING|DIGIT|NUMBER|boolean);
payload_type: DIGIT 'event' #nth_event
            | 'trace'       #trace
            ;


procedural: 'procedural' string_list 'with' procs;
procs:  'exact-subsequence'                             #exact_subseq
     | (is_exact='exact')? 'occurrence' DIGIT 'times'  #occurences
     ;

model: 'model' sat_type 'with' satswitch 'semantics over templates:' template+;
satswitch: 'VacuitySat'    #vacuity_sat
         | 'NotSat'        #not_sat
         | 'NotVacuitySat' #not_vac_sat
         | 'Sat'           #sat
         ;
sat_type: 'some' #sat_some
        | 'all'  #sat_all
        ;
template: name=STRING string_list;

boolean: 'True' #trueV
    | 'False' #falseV
    ;

string_list : '(' (STRING ',')* STRING ')';
int_list: '[' (DIGIT ',')* DIGIT ']';
number : NUMBER ;
STRING : '"' (~[\\"] | '\\' [\\"])* '"';
NUMBER : DIGIT '.' DIGIT ;
DIGIT : [0-9]+ ;
WS : [ \t\r\n]+ -> channel(HIDDEN) ;
COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '#' ~[\r\n]* -> skip ;