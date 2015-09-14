#!/usr/bin/python
#Grum is a Lisp like language 

#Inspiration from PeterNorvig's lisp interpreter in python

#The Motive is to study different facets of a programing language
#Recursion

#Tail call optmiization
#Type check
#Garbage collector 
# ...

import logging

#A function is a bunch of instructions in a different environment
class bcolors:
    HEADER = '\033[95m'
    BADBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class environment:
    " Enviroment 'or frame' for executing instructions "
    def __init__ (self):        
        #Stack of environments[dictionary]
        self.stackframe = [{}];
        self.envno = 0;
    def load(self,var):
        "Returns a varaible value or a function address"
        return self.stackframe[self.envno][var];
        
    def store(self,var,val):
        self.stackframe[self.envno][var] = val;

    def moveback(self):
        self.envno -=1;
        
    def movefront(self):
        self.envno +=1;
        
        
        


class errortrace:
    "Tracing back error"
    linenumber = 0;
    pos = 0
    category = "Syntax Error"
    stack = []
    Memory = [];
    message = "None"
    errorlevel = "FAIL";
    exp = '';
    def throw(self):
        s=''
        if self.category == "Syntax Error":
            s+= bcolors.FAIL + "Execution Failed :: Syntax Error"+"\n"
            s+= self.msg + bcolors.ENDC+"\n"
            s+=bcolors.BADBLUE+"Error @ Line : "+ str(self.linenumber)+bcolors.ENDC+"\n"
        elif self.category == "print":
            s+= bcolors.OKGREEN + self.msg + bcolors.ENDC;
        elif self.category == "Unimplemented Error":
            s =  bcolors.FAIL + "Execution Failed :: Unimplemented Error\n"
            s+= self.msg + bcolors.ENDC+"\n"
            s+= bcolors.BADBLUE+"Error @ Line : "+ str(self.linenumber)+bcolors.ENDC+"\n"
            
        else:            
            s+="Error notdefined";
        if self.category is not 'print':
            raise ValueError(s)
        else:
            print s


errors = errortrace();    
#env= environment();
env ={};


;

def validateparenthesis(exp):
    cnt = pos = 0;
    res = 0;
    for each in exp:
        cnt+=(each == '[');
        cnt-=(each ==']');
        pos +=1;
        if cnt<0:
            res = pos;
            return (res,False)
    
    return (pos, True and (cnt ==0));

def tokenize(e,r):
    l=[];
    while e[r] !=']':
        if e[r] != '[':            
            l.append(terminal(e[r]));
            r+=1;
        else:
            (r,p)= tokenize(e,r+1);
            l.append(p);
    r+=1
    return (r,l);

#Parse expressions here 
def parse(exp):
    """
    Splits input expression and asks tokenizer to tokenize them
    Returns tokenised list or throws error """
    global errors
    pos, proceed = validateparenthesis(exp);
    r =[];
    if proceed is True :
        e = exp.replace('[',' [ ').replace(']',' ] ').split();        
        (_,r) = tokenize(e,1);
    else:
        errors.msg = "FAIL: Unmatched Paranthesis "
        errors.pos = pos;
        errors.throw();
    return r;
        
def terminal(s):
    try:
        r = int(s);
        e = 'int'
    except:
        try:
            r =float(s);
            e = 'float';
        except: #variable name is else ? what happens
            r = s
            e = 'string'
            if s in ['if','?','else','var','main','end','=','+','-','*','/','%','<','>','==','!=','quote','while']:
                e = 'keyword';
    return (r,e);





#Evaluator evaluates an Expression
#An expression always returns an integer
def evaluator(stms):
    global env;
    global errors;
    
    result = None;
    logging.info('evaluating %s' + str(stms))

    if stms == []:        
        result = 0

#terminals
    
    if stms[0][1] == 'int'or stms[0][1] == 'float':
        result = stms[0][0];
    elif stms[0][1] =='string':            
        result = env[stms[0][0]];    

    #terminals
    if stms[0][1] == 'int'or stms[0][1] == 'float' or stms[0][1] == 'string':
        exp1 = stms
    #unary
    elif stms[0][0] in['?','quote']:            
        [_,exp]=stms;
        if stms[0][0] == '?':
            result = evaluator(exp);
            errors.category = 'print';
            errors.msg = str(result);
            errors.throw();
        elif stms[0][0] == 'quote':
            errors.msg ="Quotes are Unimplemented"
            errors.category ="Unimplemented Error"
            errors.throw();
    #binary
    elif stms[0][0] in ['+','-','*','/','%','>','<','==','!=','=','while']:
            [exp1,exp2] = stms[1];
            if stms[0][0] == 'while':
                while(evaluator(exp1)):
                    result = evaluator(exp2);
            if stms[0][0] == '=':                
                result = evaluator(exp2)
                env.update({exp1[0][0]:result})        
            elif stms[0][0] == '+':
                e1 = evaluator(exp1)
                e2 = evaluator(exp2)
                logging.info(e1)
                logging.info(e2)
                result = e1 + e2
            elif stms[0][0] == '-':
                    result = evaluator(exp1)- evaluator(exp2)
            elif stms[0][0] == '*':
                    result = evaluator(exp1)* evaluator(exp2)
            elif stms[0][0] == '/':
                    errors.msg = "Runtime error: Division by 0"
                    e2 = evaluator(exp2);                    
                    if  e2!=0:
                        result = evaluator(exp1)/e2;
                    else:
                        errors.throw();
            elif stms[0][0] == '>':            
                    result = True if evaluator(exp1)>evaluator(exp2) else 0;
            elif stms[0][0] == '<':
                    result = True if evaluator(exp1)<evaluator(exp2) else 0;
            elif stms[0][0] == '==':
                    result = True if evaluator(exp1) == evaluator(exp2) else 0;
                    
    #ifelse
    elif stms[0][0] == 'if' :
        try:
            [a,exp1,exp2,b,exp3] = stms;            
            assert(a[0]=='if' and b[0]=='else');
            logging.info("Parsed if else successfully ....");            
        except:
            raise SyntaxError("Incorrect if statement");
        result = evaluator(exp2) if (evaluator(exp1)==True) else evaluator(exp3);
    #Compund expressions
    elif result is None:
        logging.info('Can be Compund of expression')
        for each in stms:
            result = evaluator(each);
        #Todo : store return a value in stack
            
#Cannot resolve statement
    if result is None:
        raise SyntaxError("Incorrect statement");
    return result;

def repl():
    " Prompt- read evaluate print "
    while True:
        evaluator(parse(raw_input('grumpy : ')));

def main(argv):
    """ Welcome to grumpy, an interpreter for grum in python.
    This is a toy interpreter written as an aid to a systems course
                    Author: GR R (i.e) Gowtham Rangarjan """
    prg='';
    if '--log' in argv :
        logging.basicConfig(level=logging.INFO);
    print main.__doc__
        
    if len(argv) >=1:
        f = open(argv[0],'r');
        prg = ''
        for each in f.readlines():
            each = each.strip();
            if len(each)>=1:
                if each[0] =='#':
                    continue;
            prg+=each;
        evaluator(parse(prg));
    else:
        repl();

import sys
if __name__== '__main__':
    main(sys.argv[1:])
