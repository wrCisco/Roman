#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 Francesco Martini
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


__version__ = "0.1.0"
__author__ = "Francesco Martini"


from collections import OrderedDict


class Roman(object):
    """
    Class of roman numerals. See Roman.__init__ method for
    further details.
    """

    # if Roman.arithmetic_mode == "strict", arithmetic operations are allowed
    # only between Roman instances. Otherwise (suggested value: "tolerant")
    # they are possible with other numeric types whose integer part is
    # equal to their total value.
    arithmetic_mode = "tolerant"

    tokens = OrderedDict([
        ('I', {'value': 1, 'subtractives': ('IV', 'IX')}),
        ('IV', {'value': 4}),
        ('V', {'value': 5}),
        ('IX', {'value': 9}),
        ('X', {'value': 10, 'subtractives': ('XL', 'XC')}),
        ('XL', {'value': 40}),
        ('L', {'value': 50}),
        ('XC', {'value': 90}),
        ('C', {'value': 100, 'subtractives': ('CD', 'CM')}),
        ('CD', {'value': 400}),
        ('D', {'value': 500}),
        ('CM', {'value': 900}),
        ('M', {'value': 1000})
    ])

    def __init__(self, numeral:str, check:bool=True,
                 subtractive_notation:bool=True):
        """
        Build Roman instance from a string of characters.
        If check is False the formal correctness of the number will not
        be checked (but the string must contain only characters amongst 
        'IVXLCDM' anyway). A ValueError will be raised for invalid strings.
        Subtractive_notation set to True means that the roman numeral for,
        e.g., 99 will be 'XCIX'; subtractive_notation set to False means
        that 99 will be 'LXXXXVIIII'.
        
        >>> r1 = Roman('XLV')
        >>> r1.value
        45
        >>> r1.numeral
        'XLV'
        >>> r1.is_valid
        True
        >>> r1.subtractive_notation
        True
        >>> r1.subtractive_notation = False
        >>> r1.value
        45
        >>> r1.numeral
        'XXXXV'
        >>> r2 = Roman('XLL', check=False)
        >>> r2.value
        90
        >>> r2.is_valid
        False

        You may want to build a Roman from an integer. In that
        case you should use the int_to_roman function.

        >>> r3 = Roman(int_to_roman(349))
        >>> r3.numeral
        'CCCXLIX'

        Roman instances support many fundamental arithmetic operations
        between non negative integers. The result is another instance of the
        Roman class (whose subtractive_notation attribute value is equal to
        that of the left member of the operation). Subtractions are allowed 
        only if they have a non negative result. True division (the 'normal'
        division, exemplified below) is an alias of __divmod__ method:
        the result is a tuple whose first member is the result of the
        floor division and second member is the remainder.

        >>> add_ = r3+r1
        >>> add_.value
        394
        >>> add_.numeral
        'CCCXCIV'
        >>> div_ = r3/r1
        >>> div_[0].numeral # result
        'VII'
        >>> div_[1].numeral # remainder
        'XXXIV'

        Comparisons can be made with instances of classes that support
        the float method.

        >>> r3 >= 349.5
        False
        """

        self._numeral = None
        self.numeral = numeral.upper()
        self._subtractive_notation = None
        self.subtractive_notation = subtractive_notation
        for index, char in enumerate(self.numeral):
            if char not in Roman.tokens.keys():
                raise ValueError('{} at position {} is not a valid '
                                 'roman numeral.\n'.format(char, index))
        self.check = check
        self.check_validity(self.check)
        self._value = None
        self.value = self.roman_to_int()

    def check_validity(self, check):
        self.is_valid = self._is_valid_roman()
        if check and not self.is_valid:
            raise ValueError('{} is not a valid roman '
                             'numeral'.format(self.numeral))

    @property
    def numeral(self):
        return self._numeral

    @numeral.setter
    def numeral(self, numeral:str):
        if self._numeral is None:
            self._numeral = numeral.upper()
        else:
            old_value = self.value
            old_numeral = self._numeral
            self._numeral = numeral.upper()
            new_value = self.roman_to_int()
            if old_value != new_value:
                print("You can't change the value of Roman number. "
                      "Build new instance instead.")
                self._numeral = old_numeral

    @numeral.deleter
    def numeral(self):
        raise AttributeError("Numeral attribute must not be deleted.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, integer:int):
        if integer != self.roman_to_int():
            raise ValueError("You can't assign arbitrary values to roman "
                             "numbers already defined. Use "
                             "Roman(int_to_roman(integer)) instead.")
        else:
            self._value = integer

    @value.deleter
    def value(self):
        raise AttributeError("Value attribute must not be deleted.")

    @property
    def subtractive_notation(self):
        return self._subtractive_notation

    @subtractive_notation.setter
    def subtractive_notation(self, value:bool):
        if not isinstance(value, bool):
            raise ValueError("Value of subtractive_notation must be boolean")
        self._subtractive_notation = value
        try:
            self.numeral = int_to_roman(self.value, self.subtractive_notation)
        except AttributeError:
            pass

    @subtractive_notation.deleter
    def subtractive_notation(self):
        raise AttributeError("Subtractive_notation attribute "
                             "must not be deleted.")

    def _valid_for_arithmetic(self, other):
        if isinstance(other, self.__class__) or \
                (Roman.arithmetic_mode != "strict" and other == int(other)):
            return True
        raise ValueError("Operand must be a Roman instance or, if "
                         "Roman.arithmetic_mode (class attribute) "
                         "is different from 'strict', "
                         "must be equal to its integer value.")
    
    def __repr__(self):
        class_str = str(self.__class__)
        class_obj = class_str[class_str.index("'")+1:class_str.rindex("'")]
        return '{}("{}")'.format(class_obj, self.numeral)

    def __str__(self):
        return self.numeral

    def __bool__(self):
        if self.value:
            return True
        else:
            return False

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)
    
    def __add__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value + int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __radd__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) + self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value - int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __rsub__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) - self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __isub__(self, other):
        return self - other

    def __mul__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value * int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __rmul__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) * self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __imul__(self, other):
        return self * other

    def __floordiv__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value // int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __rfloordiv__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) // self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __ifloordiv__(self, other):
        return self // other

    def __truediv__(self, other):
        self._valid_for_arithmetic(other)
        return self.__divmod__(other)

    def __rtruediv__(self, other):
        self._valid_for_arithmetic(other)
        return self.__rdivmod__(other)

    def __itruediv__(self, other):
        return self.__divmod__(other)

    def __mod__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value % int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __rmod__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) % self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __imod__(self, other):
        return self % other

    def __divmod__(self, other):
        self._valid_for_arithmetic(other)
        result = divmod(self.value, int(other))
        return (Roman(int_to_roman(result[0],
                                   subtr_notation=self.subtractive_notation),
                      subtractive_notation=self.subtractive_notation),
                Roman(int_to_roman(result[1],
                                   subtr_notation=self.subtractive_notation),
                      subtractive_notation=self.subtractive_notation))

    def __rdivmod__(self, other):
        self._valid_for_arithmetic(other)
        result = divmod(int(other), self.value)
        return (Roman(int_to_roman(result[0],
                                   subtr_notation=self.subtractive_notation),
                      subtractive_notation=self.subtractive_notation),
                Roman(int_to_roman(result[1],
                                   subtr_notation=self.subtractive_notation),
                      subtractive_notation=self.subtractive_notation))

    def __pow__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(self.value ** int(other),
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __rpow__(self, other):
        self._valid_for_arithmetic(other)
        return Roman(int_to_roman(int(other) ** self.value,
                                  subtr_notation=self.subtractive_notation),
                     subtractive_notation=self.subtractive_notation)

    def __ipow__(self, other):
        return self ** other

    def __abs__(self):
        return self

    def __eq__(self, other):
        return self.value == float(other)

    def __ne__(self, other):
        return self.value != float(other)

    def __lt__(self, other):
        return self.value < float(other)
    
    def __le__(self, other):
        return self.value <= float(other)

    def __gt__(self, other):
        return self.value > float(other)

    def __ge__(self, other):
        return self.value >= float(other)

    def roman_to_int(self):
        """
        Get the integer value from the roman numeral of an instance
        of the class Roman. This method is used to set the value attribute
        of that instance.
        """
        integer = 0
        skip_next_char = False
        for index, char in enumerate(self.numeral):
            if skip_next_char:
                skip_next_char = False
                continue
            (present_token,
             skip_next_char,
             max_rep) = self._get_token(index, char)
            integer += Roman.tokens[present_token]['value']
        return integer

    def _is_valid_roman(self):
        """
        Check the correctness of the roman numeral. Returns True or False.
        """
        previous_token = ''
        repetitions = 0
        skip_next_char = False
        token_index = {k:i for i,k in enumerate(reversed(Roman.tokens.keys()))}

        for index, char in enumerate(self.numeral):
            if skip_next_char:
                skip_next_char = False
                continue
            (present_token,
             skip_next_char,
             max_rep) = self._get_token(index, char)
            if previous_token in ('IV', 'IX'):
                return False
            if previous_token == present_token:
                repetitions += 1
                if repetitions > max_rep and present_token != 'M':
                    return False
            else:
                repetitions = 0
                if previous_token in ('XL', 'CD'):
                    modifier = 1
                elif previous_token in ('XC', 'CM'):
                    modifier = 3
                else:
                    modifier = 0
                try:
                    if (token_index[previous_token]+modifier >
                            token_index[present_token]):
                        return False
                except KeyError:
                    pass
            previous_token = present_token
        return True

    def _get_token(self, index:int, char:str):
        """
        Get the next token (one or two characters) of the roman numeral 
        during parsing and associate to it the maximum number of times
        that the token can appear in sequence. 
        """
        skip_next_char = False
        present_token = char
        subtr = Roman.tokens[char].get('subtractives', '')
        if subtr:
            if self.subtractive_notation:
                max_rep = 2
                try:
                    next_char = self.numeral[index+1]
                except IndexError:
                    pass
                else:
                    if char+next_char in subtr:
                        present_token = char+next_char
                        skip_next_char = True
            else:
                max_rep = 3
        else:
            max_rep = 0
        return present_token, skip_next_char, max_rep


def int_to_roman(integer:int, subtr_notation:bool=True,
                 accept_negative:bool=False):
    """
    Converts an integer in a string of roman numerals.
    Typical usage might be using the result of this function
    as first argument to build an instance of the Roman class.
    If accept_negative is set to True, conversion will happen
    with negative integers also, but Roman class won't accept
    those numerals.

    >>> roman_numeral = int_to_roman(269)
    >>> print(roman_numeral)
    CCLXIX
    >>> r1 = Roman(roman_numeral)
    >>> r1.value
    269
    >>> other_roman = int_to_roman(269, subtr_notation=False)
    >>> print(other_roman)
    CCLXVIIII
    >>> r2 = Roman(other_roman, subtractive_notation=False)
    >>> r2.value
    269
    """

    if int(integer) != integer:
        raise ValueError("Invalid value for conversion: {}".format(integer))
    roman = ''
    if integer < 0:
        if accept_negative:
            roman += '-'
            integer = abs(integer)
        else:
            raise ValueError("Negative integers not allowed.")
    while integer > 0:
        for rom_val in reversed(Roman.tokens.keys()):
            if len(rom_val) == 2 and not subtr_notation:
                continue
            int_val = Roman.tokens[rom_val]['value']
            if integer >= int_val:
                roman += rom_val
                integer -= int_val
                break
    return roman


if __name__ == '__main__':
    import doctest
    doctest.testmod()
