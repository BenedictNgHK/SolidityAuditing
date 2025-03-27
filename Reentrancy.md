```
check-effects-interaction(AST node):
    require_is_called = false
    transaction_is_called = false
    protected = []
    for statements in node:
        if require is invoked and require.parameter is state_variable and require.parameter is not in protected:
            add require.parameter to protected
            require_is_called = true
            transaction_is_called = false
        if statement.type == AssignmentStatement and statement.left.var is state_variable and statement.left.var is not in protected:
            return false
        if transaction is invoked:
            protected = []
            transaction_is_called = true
    return require_is_called and transaction_is_called
```
```
is-reentrancy-guard(AST Node):
    bool if_require_invoked = false
    bool lock_first_assign = false
    bool lock_second_assign = false
    bool underline_invoked = false
    str lock_name
    if require is invoked and not if_require_invoked and check_condition(first_arguments)
        if_require_invoked = true
        lock_name = first_argument.variable
    if if_require_invoked and firstly assign value to lock and assigned_value != lock.initial_value
        lock_first_assign = true
    if if_require_invoked and lock_first_assign and underline is detected
        underline_invoked = true
    if if_require_invoked and lock_first_assign and underline_invoked and secondly assign value to lock and assigned_value == lock.initial_value
        lock_second_assign = true

    return if_require_invoked and lock_first_assign and lock_second_assign and underline_invoked and

check_condition(Expression expression):
    if expression.type == 
```