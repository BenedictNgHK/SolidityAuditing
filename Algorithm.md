CheckReentrancy(ErrorLogger logger, File file)
keyword <- ["call", "send", "transfer", "delegatecall"]
for all contract in file.contracts            
    for all function in contract.functions
        if function invokes any function in keyword
            add function to keyword
            safeContract <- Fasle
            for all modifier in function.modifers
                if modifier is Reentrancy Guard
                    safeContract <- true
                    break
            if safeContract
                continue
            if function follows CEI pattern
                continue
            
            if function.visibility is not private or internal 
                logger.log(function)
    reset keyword

CheckCEI(AST functionBody, List stateVariables)
flags["check"] <- false
flags["effects"] <- false
flags["interaction"] <- false
protectedVariables = []

for statement in functionBody
   
    if require or revert is invoked
        analyze condition
        if add new state variables to protectedVariables 
            flags["check"] <- True
        
    else if update state variables
        if(flags["interaction"] or variable is not in protectedVariables)
            return False
        if flags["check"]
            falgs["effects"] <- True
    else if statement sends ether out  and flags["check"] and flags["effects"]
        clear protectedVariables
        flags["interaction"] <- True
        flags["check"] <- False
        flags["effects"] <- False

return flags["interaction"]