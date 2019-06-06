
class AllocteRegister(object):
    def __init__(self, symtable, threeAC):
        self.symtable = symtable
        self.code = threeAC.code
        self.symbols = []

        self.unused_register = ['eax', 'ebx', 'ecx', 'edx']
        self.used_register = []

        self.blocks = []
        self.next_use = []
        self.block_label = {}
        # {[startline, endline]: label_name}

        self.register_symbol = {}
        self.symbol_register = {}

        # initialization
        for reg in self.unused_register:
            self.register_symbol[reg] = ''
        
        # add symbol
        for scope in self.symtable.table:
            scope_name = scope.name
            for var in scope.symbols.keys():
                var_entry = self.symtable.get_identifier(var)
                type_entry = self.symtable.Lookup(var_entry.typ, 'Ident')
                if var_entry != None:
                    self.symbols.append(var)
                # array？
                if var_entry.var_func == 'object':
                    for param in var_entry.params:
                        self.symbols.append(var+'_'+param[0])
                        # self.symbols.append('self_'+param[0])

            # TODO 增加临时变量        
            # if scope_name not in self.symtable.localVals.keys():
            #     self.symtable.localVals[scope_name] = []
            # self.symbols += self.symtable.localVals[scope_name]
            
            self.symbols = list(set(self.symbols))

        for sym in self.symbols:
            self.symbol_register[sym] = ''


    def block2label(self):
        '''
            map every block into a label name 
        '''
        for block in self.blocks:
            self.block_label[block] = ""
        
        for index, block in enumerate(self.blocks):
            if self.code[block[0]][1] = 'LABEL':
                label_name = self.code[block[0]][3]
                self.block_label[block] = label_name
            
            for i in range(index+1, len(self.blocks)):
                block = self.blocks[i]
                if self.code[block[0]][1] != 'LABEL':
                    self.block_label[block] = label_name
                else:
                    break

        for block in self.blocks:
            if self.block_label[block] = '':
                self.block_label = 'main' 


    def label_line(self, label_name):
        '''
            find line num by label name 
        '''
        for i in range(len(self.code)):
            if self.code[i][1] == 'LABEL':
                if self.code[i][3] == None:
                    if self.code[i][5] == label_name:
                        return self.code[i][0]
                else:
                    if self.code[i][3] == label_name:
                        return self.code[i][0]
   
    
    def block_assign(self, block_index):
        '''
            read the code in the given block from the last line to first line
            update next use 
        '''
        
        block = self.blocks[block_index]
        start, end = block
        code = self.code[start-1:end]

        for sym in self.symbols:
            preline[sym] = -1
        
        for i in range(len(code), 0, -1):
            line = {}
            code_line = code[i-1]

            lhs = code_line[2]
            op1 = code_line[3]
            op2 = code_line[4]

            if lhs in self.symbols:
                line[lhs] = -1
            if op1 in self.symbols:
                line[op1] = code_line[0]
            if op2 in self.symbols:
                line[op2] = code_line[0]
            
            for sym in self.symbols:
                if sym not in code_line:
                    line[sym] = preline[sym]
                
            self.next_use[block_index].append(line)
            preline = line.copy()

        self.next_use[block_index] = list(reversed(self.next_use[block_index]))


    def get_block_maxuse(self, block_index, line_num):
        '''
            return the symbol with maximum value of next use
        '''
        start = self.blocks[block_index][0]
        nextuse =  self.next_use[block_index][line_num+1-start]

        for sym in self.symbols:
            if self.symbol_register[sym] != '' and float(nextuse[sym])>max_use:
                max_use = float(nextuse[sym])
                max_sym = sym
        
        return max_sym


    def allocate_register(self, block_index, line, all_mem=False):
        code_line = self.code[line-1]
        
        # lhs = op1 OP op2
        lhs = code_line[2].name if isinstance(code_line[2], SymTableEntrt) else code_line[2]
        op1 = code_line[3].name if isinstance(code_line[2], SymTableEntrt) else code_line[3]
        op2 = code_line[4].name if isinstance(code_line[2], SymTableEntrt) else code_line[4]
        
        #if lhs not in self.symbols:

        if (line<self.blocks[block_index][1]):
            next_use_block = self.next_use[block_index][line+1 - self.blocks[block_index][0]] 
        else:
            next_use_block = {}
            for sym in self.symbols:
                next_use_block[sym] = -1

        if op1 in self.symbols and self.symbol_register[op1]!='' and next_use_block == -1:
            reg = self.symbol_register[op1]

        elif op2 in self.symbols and self.symbol_register[op2]!='' and next_use_block == -1:
            reg = self.symbol_register[op2]

        elif len(self.unused_register)>0:
            reg = self.unused_register[0]
            self.unused_register.remove(reg)
            self.used_register.append(reg)
        
        elif next_use_block[lhs]!=-1 or all_mem =True:
            var = self.get_block_maxuse(block_index, line)
            reg = self.symbol_register[var]
        
        else:
            reg = lhs
        return (reg, _)
          





