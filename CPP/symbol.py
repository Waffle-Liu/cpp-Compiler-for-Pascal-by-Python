import sys
import json
from functools import wraps


def list_format(list, indent=4):
    '''格式化输出用函数'''

    return '[%s%s%s]' % (
        '\n' + ' '*indent if len(list) > 1 else '',
        (',' + '\n' + ' '*indent).join(
            str(item).replace('\n', '\n' + ' ' * indent)
            for item in list),
        '\n' if len(list) > 1 else ''
    )


def singleton(cls):
    '''单例模式'''

    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    return _singleton


class Symbol:
    '''符号类'''

    def _get_size(self):
        '''计算一个符号的大小'''

        simple = {
            'integer': 4,
            'real': 8,
            'char': 1,
            'boolean': 1,
        }

        if self.var_function == 'function':
            return 0

        elif self.type in simple:
            return simple[self.type]

        elif self.type == 'array':
            size = Symbol(None, self.params['data_type']).size

            for (start, end) in self.params['dimension']:
                size *= end - start + 1

            return size

        elif self.type == 'record':
            size = 0
            for name, type in self.params:
                size += Symbol(name, type).size

            return size

        else:
            t = Table()
            symbol = t.get_identifier(self.type)
            if symbol.var_function != 'type':
                sys.exit('`%s` is not a type. ' % self.type)

            return symbol.size

    def __init__(self, name, type, var_function="var", offset=0, params=None):
        '''初始化一个符号

        name:           符号名

        type:           one of 'integer', 'real', 'char', 'boolean', 'array', 'record', or existing type
                        如果是函数，那么该字段表示它的返回值类型（函数只支持基础类型）

        var_function:   one of 'var', 'const', 'function', 'type'

        offset:         该符号位于对应的作用域中的偏移量

        params:         如果是 function，那么 params 依照一下的 list 传递参数列表：
                        [
                            (arg1, type1),
                            (arg2, type2),
                            ...
                        ]
                        如果是 array，那么 params 依照以下的 dict 传递数据类型和范围：
                        {
                            'data_type': 'integer',
                            'dimension': [(0, 100), (0, 1000), ...]
                        }
                        如果是 record 那么 params 依照以下的 list 传递结构：
                        [
                            (name1, type1),
                            (name2, type2),
                            ...
                        ] 
                        其中 type 可能是复杂类型
        '''

        self.name = name
        self.type = type
        self.var_function = var_function
        self.offset = offset
        self.params = params
        self.size = self._get_size()

    def __str__(self):
        return 'Symbol(`%s`, %s, %s)' % (
            str(self.name),
            str(self.type),
            str(self.var_function))


class Scope:
    '''作用域类'''

    def __init__(self, name=None, type=None, return_type=None, width=0):
        self.name = name
        self.type = type
        self.return_type = return_type
        self.width = width

        self.symbols = {}
        self.temps = {}

        self.label_number = 0

    def __str__(self):
        return 'Scope(`%s`, symbols=%s)' % (
            str(self.name),
            list_format(list(self.symbols.values())),
        )

    def define(self, name, type, var_function='var', params=None):
        '''定义一个新符号'''
        if name in self.symbols:
            sys.exit('Name `%s` is already defined. ' % name)

        symbol = Symbol(name, type, var_function,
                        offset=self.width, params=params)
        self.symbols[name] = symbol

        if var_function in ('var', 'const'):
            self.width += symbol.size

        return symbol

    def temp(self, type, var_function='var', params=None):
        '''申请一个临时符号'''
        name = '_t%06d' % len(self.temps)

        symbol = Symbol(name, type, var_function,
                        offset=self.width, params=params)

        self.temps[name] = symbol

        return symbol

    def label(self):
        '''申请一个 label'''
        name = '_l%06d' % self.label_number
        self.label_number += 1
        return name

    def get(self, name):
        '''查找一个符号'''
        if name in self.symbols:
            return self.symbols[name]
        if name in self.temps:
            return self.temps[name]

        raise ValueError('Name `%s` is not defined in scope `%s' %
                         (name, self.name))


@singleton
class Table:
    '''符号表类'''

    def __init__(self):
        '''符号表用一个栈表示，其中每一个为一层 scope。

        初始只有一层 main。
        临时变量全部放在 temp 中。
        '''

        self.table = [Scope('main', type='function')]
        self.temp = Scope('temp', type='function')

    def __str__(self):
        return 'Table(%s)' % list_format(self.table)

    def get_current_scope_name(self):
        '''获得当前作用域名'''
        return self.table[-1].name

    def get_identifier(self, name, index=None):
        '''按照作用域依次查找一个名字'''

        if index is None:
            index = len(self.table) - 1
        if index == -1:
            return None

        scope = self.table[index]

        if name in scope.symbols:
            return scope.symbols[name]
        else:
            return self.get_identifier(name, index - 1)

    def set_identifier(self, name, type, var_function='var', params=None):
        '''定义一个新名字'''
        return self.table[-1].define(name, type, var_function, params)

    define = set_identifier

    def get_temp(self, type, var_function='var', params=None):
        return self.table[-1].temp(type, var_function, params)

    def get_label(self):
        return self.table[-1].label()

    def add_scope(self, name, type, return_type):
        '''增加一层作用域'''
        scope = self.table[-1]
        self.table.append(Scope(
            name='%s.%s' % (scope.name, name),
            type=type,
            return_type=return_type))

    def del_scope(self):
        '''删除一层作用域'''
        return self.table.pop()


if __name__ == '__main__':
    t = Table()
    t.define('IDCard', 'record', 'type', [
        ('ID', 'integer'),  # 4
        ('name', 'char')  # 1
    ])
    t.define('Student', 'record', 'type', [
        ('name', 'char'),  # 1
        ('card', 'IDCard')  # 4 + 1
    ])
    t.define('CircleLin', 'Student', 'var')
    t.define('students', 'array', 'var', {
        'data_type': 'Student',  # 1 + (4+1)
        'dimension': [(1, 100)]  # 100
    })
    print(t.get_identifier('students').size)  # (1 + (4+1)) * 100