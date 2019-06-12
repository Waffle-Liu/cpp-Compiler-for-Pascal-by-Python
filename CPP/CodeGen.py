from Rule import op32_dict, op32_dict_i, register_list, binary_list
from symbol_table import Symbol


class CodeGen():
    def __init__(self, symtable, threeAC, allocReg):
        self.symtable = symtable
        self.threeAC = threeAC
        self.allocReg = allocReg

        self.code = threeAC.code
        self.asmcode = []
        self.symbol_register = self.allocReg.symbol_register
        self.register_symbol = self.allocReg.register_symbol

        self.allocReg.get_basic_block()
        self.allocReg.iterate_block()

        # self.allocReg.block2label()

        # self.handle_binary(self.code[23])
        # self.handle_binary(self.code[24])
        # for i in range(11):
        #     self.handle_binary(self.code[i])
        self.tacToasm()

        self.display_asm()

    def handle_term(self, op, block_index, line_num):
        
        out = None
        if isinstance(op, Symbol):
            out = self.allocReg.getReg(op, block_index, line_num)
        elif isinstance(op, int):
            out = op
        elif isinstance(op, str):
            out = ord(op)
        elif isinstance(op, bool):
            out = [False, True].index(op)
        return out

    def handle_binary(self, codeline):
        self.asmcode.append('\n# handle_binary')

        line_num, operation, lhs, op1, op2 = codeline
        block_index = self.allocReg.line_block(line_num)
        reg_op1 = self.handle_term(op1, block_index, line_num)
        reg_op2 = self.handle_term(op2, block_index, line_num)
        reg_lhs = self.handle_term(lhs, block_index, line_num)

        if type(op1) != int and type(op2) != int:
            inst = op32_dict[operation]
        else:
            inst = op32_dict_i[operation]

        const_type = [int, str, bool]

        if type(op1) in const_type and type(op2) in const_type:

            const = eval(str(op1)+' '+operation.lower()+' '+str(op2))
            self.asmcode.append(inst+' '+reg_lhs+', '+'$zero, '+str(const))

        elif type(op1) == Symbol and type(op2) in const_type:
            const = reg_op2
            self.asmcode.append(inst+' '+reg_lhs+', '+reg_op1+', '+str(const))

        elif type(op1) == Symbol and type(op2) == Symbol:
            self.asmcode.append(inst+' '+reg_lhs+', '+reg_op1+', '+reg_op2)

    def handle_division(self, codeline):
        print("[This line]: ", codeline)
        pass

    def handle_input(self, codeline):
        self.asmcode.append('\n# handle_input')
        line_num, operation, lhs, op1, op2 = codeline
        block_index = self.allocReg.line_block(line_num)
        reg_lhs = self.handle_term(lhs, block_index, line_num)

        # TODO 只考虑输入整数
        self.asmcode.append('li $v0, 5')  # read int
        self.asmcode.append('syscall')
        self.asmcode.append('addi ${}, $v0, 0'.format(reg_lhs))

    def handle_print(self, codeline):
        self.asmcode.append('\n# handle_print')

        line_num, operation, lhs, op1, op2 = codeline
        block_index = self.allocReg.line_block(line_num)

        if type(op1) == Symbol:
            reg_op1 = self.handle_term(op1, block_index, line_num)
            print(op1, reg_op1)
            # TODO 只考虑输出整数
            self.asmcode.append('li $v0, 1')
            self.asmcode.append('addi $a0, {}, 0'.format(reg_op1))
            self.asmcode.append('syscall')

        else:
            # TODO 只考虑输出整数
            self.asmcode.append('li $v0, 1')
            self.asmcode.append('addi $a0, $0, {}'.format(op1))
            self.asmcode.append('syscall')

    def handle_cmp(self, codeline):
        print("[This line]: ", codeline)
        pass

    def handle_jmp(self, codeline):
        print("[This line]: ", codeline)
        pass

    def handle_label(self, codeline):
        self.asmcode.append('\n# handle_label')
        print("[*** This line]: ", codeline)
        # TODO: 保存ra，保存所有寄存器（临时寄存器和s寄存器）

        bassAddr = str(self.symtable[codeline[3]].width)

        for index in range(8):
            # SW R1, 0(R2)
            self.asmcode.append('SW'+ ' t' + str(index) + ' (' + bassAddr + ')$sp')


        if codeline[3] != None:
            # TODO: 分配内存
            self.asmcode.append(codeline[2]+':')
            self.asmcode.append('addi'+ ' ' + '$sp $sp' + ' -' + str(self.symtable[codeline[3]].width))

            pass 
            # codeline[]
        else:
            # 真的是一个label
            self.asmcode.append(codeline[2]+':')
            # self.asmcode.append(inst+' '+reg_lhs+', '+reg_op1+', '+str(const))
            pass
        pass

    def handle_call(self, codeline):
        print("[This line]: ", codeline)
        # TODO: 访问链：判断两个scope之间的关系
        parent
        if parent:
            # 等于

            
            pass
        else:
            # 它parent的
            pass 


        # TODO: 控制链
         = $fp

        # TODO: ra
        sw  $ra -8($sp)

        # TODO: reg
        for index in range(8,24):
            # SW R1, 0(R2)
            self.asmcode.append("SW $%s, %d($sp)"%(index, -12 - (index-8)*4)

        # TODO: param


        # TODO
        self.asmcode.append('addi $sp $sp %d'%( - self.symtable[codeline[4]].width) - 76)

        # jal
        self.asmcode.append("jal %s"%(self.symtable[codeline[3]])

        pass

    def handle_params(self, codeline):
        print("[This line]: ", codeline)


    def handle_return(self, codeline):
        self.asmcode.append('\n# handle_return')
        print("[This line]: ", codeline)
        # FIXME: 需要填好返回值，然后放回ra，最后返还stack上分配的内存，返回

        # TODO: 指针

        # TODO 恢复参数 （引用传递
        
        # TODO 恢复寄存器

        # TODO 恢复返回地址 ra

        # TODO ra'




        self.asmcode.append('addi'+ ' ' + '$sp $sp' + ' +' + str(self.symtable[codeline[3]].width))
        self.asmcode.append('jr $ra')
        pass

    def handle_loadref(self, codeline):
        print("[This line]: ", codeline)
        pass

    def handle_storeref(self, codeline):
        print("[This line]: ", codeline)
        print(codeline)
        pass

    def tacToasm(self):
        for codeline in self.code:
            operation = codeline[1]
            if operation in binary_list:
                self.handle_binary(codeline)
            elif operation in ['BNE', 'BEQ', 'JMP']:
                self.handle_cmp(codeline)
            elif operation == 'LABEL':
                self.handle_label(codeline)
            elif operation == 'CALL':
                self.handle_call(codeline)
            elif operation == 'PARAM':
                self.handle_params(codeline)
            elif operation == 'RETURN':
                self.handle_return(codeline)
            elif operation == 'INPUT':
                self.handle_input(codeline)
            elif operation in ['PRINT', 'PRINTLN']:
                self.handle_print(codeline)
            elif operation == 'LOADREF':
                self.handle_loadref(codeline)
            elif operation == 'STOREREF':
                self.handle_storeref(codeline)

    def display_asm(self):
        for line in self.asmcode:
            print(line)
