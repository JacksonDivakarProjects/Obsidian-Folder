
|Precedence|Category|Operators|Associativity|
|---|---|---|---|
|**1**|Postfix|`expr++` `expr--` `() (function call)` `[] (array subscripting)` `.` `->`|**Left to Right**|
|**2**|Unary|`++expr` `--expr` `+` `-` `!` `~` `(type)` `*` `&` `sizeof` `_Alignof`|**Right to Left**|
|**3**|Multiplicative|`*` `/` `%`|Left to Right|
|**4**|Additive|`+` `-`|Left to Right|
|**5**|Shift|`<<` `>>`|Left to Right|
|**6**|Relational|`<` `<=` `>` `>=`|Left to Right|
|**7**|Equality|`==` `!=`|Left to Right|
|**8**|Bitwise AND|`&`|Left to Right|
|**9**|Bitwise XOR|`^`|Left to Right|
|**10**|Bitwise OR|`|`|
|**11**|Logical AND|`&&`|Left to Right|
|**12**|Logical OR|`||
|**13**|Conditional (Ternary)|`?:`|**Right to Left**|
|**14**|Assignment|`=` `+=` `-=` `*=` `/=` `%=` `<<=` `>>=` `&=` `^=` `|=`|
|**15**|Comma|`,`|Left to Right|