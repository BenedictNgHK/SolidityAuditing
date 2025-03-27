from solidity_parser import parser
import pprint
import copy
import solidity_parser
class AuditReentrancy:
    def __init__(self, node):
        self.node = node
        self.vulnerability = 'Reentrancy'
    def checkKeyword(self, node):
        if not isinstance(node, dict):
            return False
        if node.get('type') == 'IfStatement':
            # pprint.pprint(node)
            value = self.checkKeyword(node.TrueBody) or self.checkKeyword(node.FalseBody) or self.checkKeyword(node.condition)
            return value
        if node.get('type') == 'MemberAccess':
            member_name = node.get('memberName')
            if member_name in ['call', 'send', 'transfer', 'delegatecall']:
                return True
        # return False

    # Recursively check all child nodes
        for key, value in node.items():
            if isinstance(value, list):
                for item in value:
                    if self.checkKeyword(item):
                        return True
            else:
                if self.checkKeyword(value):
                    return True

        return False
    def checkCondition(self, argument, stateVariablesList) ->bool:
        if argument.type == 'UnaryOperation' and argument.operator == '!' and   (stateVariablesList[argument.subExpression.name].expression == None or stateVariablesList[argument.subExpression.name].expression.value == False): 
            return True
        elif argument.type =='Identifier':
            if argument.name not in stateVariablesList:
                return False
            if stateVariablesList[argument.name].expression == None:
                return False
            elif  stateVariablesList[argument.name].expression.value == True:
                return True
            else:
                return False
        elif argument.type == 'BinaryOperation':
            
            if argument.operator == '==':
                
                if isinstance(argument.left, dict) and 'name' in argument.left:
                    if argument.left.name not in stateVariablesList:
                        return False
                    if stateVariablesList[argument.left.name].expression != None:
                        if(stateVariablesList[argument.left.name].expression.type=='BooleanLiteral'):
                            left = stateVariablesList[argument.left.name].expression.value
                            right = argument.right.value
                        else:
                            left = stateVariablesList[argument.left.name].expression.number
                            right = argument.right.number
                    else:
                        if(stateVariablesList[argument.left.name].typeName.name=='bool'):
                            left = False
                            right = argument.right.value
                        else:
                            left = '0'
                            right = argument.right.number
                    
                    if left == right:
                        return True
                    else:
                        return False
                elif isinstance(argument.right, dict) and 'name' in argument.right:
                    if argument.right.name not in stateVariablesList:
                        return False
                    if stateVariablesList[argument.right.name].expression != None:
                        if(stateVariablesList[argument.right.name].expression.type=='BooleanLiteral'):
                            right = stateVariablesList[argument.right.name].expression.value
                            left = argument.left.value
                        else:
                            right = stateVariablesList[argument.right.name].expression.number
                            left = argument.left.number
                    else:
                        if(stateVariablesList[argument.right.name].typeName.name=='bool'):
                            right = False
                            left = argument.left.value
                        else:
                            right = '0'
                            left = argument.left.number
                    if left == right:
                        return True
                    else:
                        return False
                else:
                    return False
            else: 
                if isinstance(argument.left, dict) and 'name' in argument.left:
                
                    if stateVariablesList[argument.left.name].expression != None:
                        if(stateVariablesList[argument.left.name].expression.type=='BooleanLiteral'):
                            left = stateVariablesList[argument.left.name].expression.value
                            right = argument.right.value
                        else:
                            left = stateVariablesList[argument.left.name].expression.number
                            right = argument.right.number
                    else:
                        if(stateVariablesList[argument.left.name].typeName.name=='bool'):
                            left = False
                            right = argument.right.value
                        else:
                            left = '0'
                            right = argument.right.number
                    if left != right:
                        return True
                    else:
                        return False
                elif isinstance(argument.right, dict) and 'name' in argument.right:
                    if stateVariablesList[argument.right.name].expression != None:
                        if(stateVariablesList[argument.right.name].expression.type=='BooleanLiteral'):
                            right = stateVariablesList[argument.right.name].expression.value
                            left = argument.left.value
                        else:
                            right = stateVariablesList[argument.right.name].expression.number
                            left = argument.left.number
                    else:
                        if(stateVariablesList[argument.right.name].typeName.name=='bool'):
                            right = False
                            left = argument.left.value
                        else:
                            right = '0'
                            left = argument.left.number

                    if left != right:
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return False
    def getLockName(self, node) -> str:
        if node.type == 'BinaryOperation':
            if isinstance(node.left, dict) and 'name' in node.left:
                return node.left.name
            elif isinstance(node.right, dict) and 'name' in node.right:
                return node.right.name
            else:
                return ''
        if node.type == 'Identifier':
            return node.name
        if node.type == 'UnaryOperation' and node.operator == '!':
            return node.subExpression.name

    def functionCallHandlerGuard(self, expression, stateVariablesList,contract,storageVariable,initialValues) -> bool:
        ret_val = False
        
        if(isinstance(expression,dict) and "expression" in expression and expression.expression.type == "FunctionCall"):
                
                if isinstance(expression.expression.expression,dict) and "name" not in expression.expression.expression:
                    pass
                else:
                    if "name" not in expression.expression.expression:
                        return ret_val
                    if expression.expression.expression.name not in self.node.contracts[contract].functions:
                        pass
                    else:
                        
                        self.isReentrancyGuard(node=self.node.contracts[contract].functions[expression.expression.expression.name]._node, contract=contract,stateVariablesList=stateVariablesList,storageVariable=storageVariable,initialValues=initialValues)
                        ret_val = True
        return ret_val
    def storageVariableHandler(self, node, storageVariable=dict()):
        if node.initialValue != None and node.initialValue.type == "TupleExpression":
            for  index,variable in enumerate(node.initialValue.components):
                if  hasattr(node.variables[index].decl.storageLocation(),"getText")and node.variables[index].decl.storageLocation().getText() == 'storage':
                    storageVariable[node.variables[index].name]= variable
        else:
            if node.variables[0].storageLocation == "storage":
                storageVariable[node.variables[0].name] = node.initialValue
                
            
            

    def isReentrancyGuard(self,node, contract,stateVariablesList,storageVariable=dict(),initialValues=dict(
        require_invoked = False,
        underline_invoked = False,
        lock_first = False,
        lock_second = False,
        lock_name = None,
        lock_first_value=None,
        initialValue=None)) -> bool:

        if (type(node) is list):
            statements = node
        elif(node.type =='FunctionDefinition' or node.type == 'ModifierDefinition'):
            statements = node.body.statements
        elif (node.type == 'Block'):
            statements = node.statements
        for index, expression in enumerate(statements):
            if expression is None:
                continue
            if "type" in expression and expression.type == 'VariableDeclarationStatement':
                
                self.storageVariableHandler(expression,storageVariable)
                continue
            if expression.type == 'IfStatement':
                initialValues_true_body = copy.deepcopy(initialValues)
                initialValues_true_body = copy.deepcopy(initialValues)
                storage_variables_true_body = copy.deepcopy(storageVariable)
                storage_variables_false_body = copy.deepcopy(storageVariable)
                if isinstance(expression.TrueBody,dict) and ("statements" or "expression" in expression.TrueBody):
                    
                    if expression.TrueBody.type == "RevertStatement" and not initialValues["require_invoked"]:
                        
                        initialValues["require_invoked"] = True
                        initialValues["lock_name"] = self.getLockName(expression.condition)
                        if initialValues["lock_name"] not in stateVariablesList:
                            continue
                        if stateVariablesList[initialValues["lock_name"]].typeName.name == "bool":
                            
                            if stateVariablesList[initialValues["lock_name"]].expression != None:
                                if "value" in stateVariablesList[initialValues["lock_name"]].expression:
                                    initialValues["initialValue"]=stateVariablesList[initialValues["lock_name"]].expression.value
                                   
                                elif "name" in stateVariablesList[initialValues["lock_name"]].expression:
                                    
                                    initialValues["initialValue"]=stateVariablesList[initialValues["lock_name"]].expression.name
                                    
                            else:
                                initialValues["initialValue"]=False
                        else:
                            
                            if stateVariablesList[initialValues["lock_name"]].expression != None:
                                if "number" in stateVariablesList[initialValues["lock_name"]].expression:
                                    initialValues["initialValue"] = stateVariablesList[initialValues["lock_name"]].expression.number
                                elif "name" in stateVariablesList[initialValues["lock_name"]].expression:
                                    initialValues["initialValue"] = stateVariablesList[initialValues["lock_name"]].expression.name
                            else:
                                initialValues["initialValue"] = '0'

                        continue
                    elif "expression" in expression.TrueBody:
                        expressions = [expression.TrueBody.expression]
                    elif "statements" in expression.TrueBody:
                        expressions = []
                        revert_invoked = False
                        for exp in expression.TrueBody.statements:
                            if exp.type == "RevertStatement": 
                                
                                revert_invoked = True    
                                break
                            expressions.append(exp)
                        if(revert_invoked and not initialValues["require_invoked"]):
                            initialValues["require_invoked"] = True
                            initialValues["lock_name"] = self.getLockName(expression.condition)
                            if initialValues["lock_name"] not in stateVariablesList:
                                continue
                            if stateVariablesList[initialValues["lock_name"]].typeName.name == "bool":
                                if stateVariablesList[initialValues["lock_name"]].expression != None:
                                    if "value" in stateVariablesList[initialValues["lock_name"]].expression:
                                        initialValues.initialValue = stateVariablesList[initialValues["lock_name"]].expression.value
                                    elif "name" in stateVariablesList[initialValues["lock_name"]].expression:
                                        initialValues.initialValue = stateVariablesList[initialValues["lock_name"]].expression.name
                                else:
                                    initialValues["initialValue"]=False
                            else:
                                if stateVariablesList[initialValues["lock_name"]].expression != None:
                                    if "number" in stateVariablesList[initialValues["lock_name"]].expression:
                                        initialValues["initialValue"] = stateVariablesList[initialValues["lock_name"]].expression.number
                                    elif "name" in stateVariablesList[initialValues["lock_name"]].expression:
                                        initialValues["initialValue"] = stateVariablesList[initialValues["lock_name"]].expression.name
                                else:
                                    initialValues["initialValue"] = '0'

                    continue
                                    
                    
            if hasattr(expression,'expression') and expression.expression.type == 'FunctionCall':
                
                function_call = expression.expression
                if(self.functionCallHandlerGuard(expression,stateVariablesList,contract,storageVariable,initialValues)):
                    continue
                if hasattr(function_call,'expression') and function_call.expression.name == 'require' and function_call.expression.type == 'Identifier' and self.checkCondition(function_call.arguments[0],stateVariablesList) and not initialValues["require_invoked"]:
                    
                    
                    initialValues["require_invoked"] = True
                    initialValues["lock_name"] = self.getLockName(function_call.arguments[0])
                    if stateVariablesList[initialValues["lock_name"]].typeName.name == "bool":
                        if stateVariablesList[initialValues["lock_name"]].expression != None:
                            initialValues["initialValue"]=stateVariablesList[initialValues["lock_name"]].expression.value
                        else:
                            initialValues["initialValue"]=False
                    else:
                        if stateVariablesList[initialValues["lock_name"]].expression != None:
                            initialValues["initialValue"] = stateVariablesList[initialValues["lock_name"]].expression.number
                        else:
                            initialValues["initialValue"] = '0'
                        

            if expression.expression.type == 'Identifier' and expression.expression.name == '_' and initialValues["require_invoked"] and initialValues["lock_first"]:
                initialValues["underline_invoked"] = True
                
            if expression.expression.type == 'BinaryOperation' and initialValues["require_invoked"] == True:
                
                if "name" in expression.expression.left and expression.expression.left.name == initialValues["lock_name"] and expression.expression.left.type == 'Identifier':
                    if initialValues["lock_first_value"] == None and expression.expression.right.type=='BooleanLiteral':
                        if expression.expression.right.value != initialValues["initialValue"]:
                            
                            initialValues["lock_first_value"] = expression.expression.right.value
                            initialValues["lock_first"] = True
                        
                    elif initialValues["lock_first_value"]== None and expression.expression.right.type=='NumberLiteral':
                      
                        if expression.expression.right.number != initialValues["initialValue"]:
                            initialValues["lock_first_value"] = expression.expression.right.number
                            initialValues["lock_first"] = True
                            
                    elif initialValues["lock_first_value"]== None and expression.expression.right.type=='Identifier':
                        if stateVariablesList[expression.expression.right.name] != initialValues["initialValue"]:
                            if(stateVariablesList[expression.expression.right.name].typeName.name != "bool"):
                                initialValues["lock_first_value"] = stateVariablesList[expression.expression.right.name].expression.number
                            else:
                                initialValues["lock_first_value"] = stateVariablesList[expression.expression.right.name].expression.value
                            if initialValues["initialValue"] != initialValues["lock_first_value"]:
                                initialValues["lock_first"] = True
                        
                    elif initialValues["require_invoked"] and initialValues["underline_invoked"] and initialValues["lock_first"]:
                        
                        if expression.expression.right.type == 'BooleanLiteral' and expression.expression.right.value == initialValues["initialValue"]:
                            initialValues["lock_second"] = True
                            continue
                        elif expression.expression.right.type=='NumberLiteral' and expression.expression.right.number == str(initialValues["initialValue"]):
                            initialValues["lock_second"] = True
                            continue
                        elif expression.expression.right.type=="Identifier":
                            if stateVariablesList[expression.expression.right.name].typeName.name == "bool":
                                if stateVariablesList[expression.expression.right.name].expression == None:
                                    value = False
                                else:
                                    value =  stateVariablesList[expression.expression.right.name].expression.value
                            else:
                                if stateVariablesList[expression.expression.right.name].expression == None:
                                    value = 0
                                else:
                                    value =  stateVariablesList[expression.expression.right.name].expression.number
                            if value == initialValues["initialValue"]:
                                initialValues["lock_second"] = True
                                continue
            # Update state variables or storage variables after protected critical section, return False
            if initialValues["require_invoked"] and initialValues["underline_invoked"] and initialValues["lock_first"] and initialValues["lock_second"]:
                if "expression" in expression:
                    if expression.expression.type == "UnaryOperation":
                        subExpression=expression.expression.subExpression
                        if "name" in subExpression:
                            if subExpression.name in stateVariablesList or subExpression.name in storageVariable:
                                return False
                            else:
                                pass
                        elif subExpression.base.name in stateVariablesList or subExpression.base.name in storageVariable:
                            return False
                            
                    if expression.expression.type == "BinaryOperation":
                        left = expression.expression.left
                        if "name" in left and (left.name in stateVariablesList or left.name in storageVariable):
                            return False
                        elif left.base.name in stateVariablesList or left.base.name in storageVariable:
                            return False
                    
        return initialValues["require_invoked"] and initialValues["underline_invoked"] and initialValues["lock_first"] and initialValues["lock_second"]
    
    def ifInteraction(self, node) -> bool:
        if node.type == 'MemberAccess' and (node.memberName == 'transfer' or node.memberName == 'send' or node.memberName == 'call' or node.memberName == 'delegatecall'):
            return True
        return False
    def addProtectedVariables(self,node,protectedVariables, stateVariablesList):
        if isinstance(node, dict) and 'left' in node:
            if (node.left.type == 'IndexAccess' and "name" in node.left.base) and (node.left.base.name in  stateVariablesList.keys()) and (node.left.base.name not in protectedVariables):
                protectedVariables.append(node.left)
            if(node.left.type == 'Identifier') and (node.left.name in stateVariablesList.keys()) and (node.left.name not in protectedVariables):
                protectedVariables.append(node.left.name)
        if isinstance(node, dict) and 'right' in node:
            if (node.right.type == 'IndexAccess') and (node.right.base.name in  stateVariablesList.keys()) and (node.right.base.name not in protectedVariables):
                protectedVariables.append(node.right)
            if(node.right.type == 'Identifier') and (node.right.name in stateVariablesList.keys()) and (node.right.name not in protectedVariables):
                
                protectedVariables.append(node.right.name)
        if node.type == 'Identifier':
            
            protectedVariables.append(node.name)
    def functionCallHandlerCEI(self, expression, stateVariablesList,contract,flags, storageVariable,protected_state_variables) -> bool:
        ret_val = False
        if(isinstance(expression,dict) and "expression" in expression and expression.expression.type == "FunctionCall"):
                
                if isinstance(expression.expression.expression,dict) and "name" not in expression.expression.expression:
                    pass
                else:
                    if "name" not in expression.expression.expression:
                        return ret_val
                    if expression.expression.expression.name not in self.node.contracts[contract].functions:
                        pass
                    else:
                        self.checkEffectsInteraction(self.node.contracts[contract].functions[expression.expression.expression.name]._node, stateVariablesList,contract,flags,storageVariable=storageVariable,protected_state_variables=protected_state_variables)
                        ret_val = True
        return ret_val
    
    def checkEffectsInteraction(self, node, stateVariablesList,contract,flags=dict(check=False,interaction=True),storageVariable=dict(),protected_state_variables = []) -> bool:
        
        if (type(node) is list):
            statements = node
        elif(node.type =='FunctionDefinition'):
            statements = node.body.statements
        elif (node.type == 'Block'):
            statements = node.statements
        
        for index ,expression in enumerate(statements):
            if expression.type == 'VariableDeclarationStatement':
                
                if expression.initialValue != None and expression.initialValue.type == "FunctionCall":
                    if_interaction = False
                    if type(expression.initialValue.expression) is list:
                        for exp in expression.initialValue.expression:
                            if hasattr(exp,'type') and self.ifInteraction(exp):
                                if_interaction = True
                                break
                    else:
                        if hasattr(expression.initialValue.expression,'type') and self.ifInteraction(expression.initialValue.expression):
                            if_interaction = True
                    if if_interaction:
                        if flags["interaction"] == True:
                            return False
                        protected_state_variables.clear()
                        flags["interaction"] = True
                    else:
                        self.functionCallHandlerCEI(expression, stateVariablesList,contract,flags,storageVariable=storageVariable,protected_state_variables=protected_state_variables)
                        self.storageVariableHandler(expression,storageVariable)
                else:
                    self.storageVariableHandler(expression,storageVariable)
                continue
            if expression.type == 'IfStatement':
                true_body = None
                false_body = None
                
                protected_state_variables_true_body = copy.deepcopy(protected_state_variables)
                protected_state_variables_false_body = copy.deepcopy(protected_state_variables)
                flags_true_body = copy.deepcopy(flags)
                flags_false_body = copy.deepcopy(flags)
                storage_variables_true_body = copy.deepcopy(storageVariable)
                storage_variables_false_body = copy.deepcopy(storageVariable)
                if isinstance(expression.TrueBody,dict) and ("statements" or "expression" in expression.TrueBody):
                    # len_first = len(protected_state_variables)
                    #     # self.addProtectedVariables(expression.condition,protected_state_variables, stateVariablesList)
                    # len_second = len(protected_state_variables)
                    # if (len_first != len_second):
                    #     flags["check"] = True
                    #     flags["interaction"] = True
                    if expression.TrueBody.type == "RevertStatement":
                        len_first = len(protected_state_variables)
                        self.addProtectedVariables(expression.condition,protected_state_variables, stateVariablesList)
                        len_second = len(protected_state_variables)
                        if (len_first != len_second):
                            flags["check"] = True
                            flags["interaction"] = True
                        continue
                    pprint.pprint(expression.TrueBody)
                    if "expression" in expression.TrueBody:
                        expressions = [expression.TrueBody.expression]
                    elif "statements" in expression.TrueBody:
                    
                        expressions = []
                        revert_invoked = False
                        for exp in expression.TrueBody.statements:
                            if exp is None:
                                continue
                            if(exp.type == "RevertStatement"):
                                revert_invoked = True
                                break
                            expressions.append(exp)
                        if(revert_invoked):
                            len_first = len(protected_state_variables)
                            self.addProtectedVariables(expression.condition,protected_state_variables, stateVariablesList)
                            len_second = len(protected_state_variables)
                            if (len_first != len_second):
                                flags["check"] = True
                                flags["interaction"] = True
                            continue
                        i = index+1
                        while(i < len(statements)):
                            expressions.append(statements[i])
                            i += 1
                    else:
                        expressions = []
                    true_body = self.checkEffectsInteraction(expressions,stateVariablesList,contract,flags_true_body,storageVariable=storage_variables_true_body,protected_state_variables=protected_state_variables_true_body)        
                    
                if isinstance(expression.FalseBody,dict) and ("statements" or "expression" in expression.FalseBody):
                   
                    if "expression" in expression.FalseBody:
                        expressions = [expression.FalseBody.expression]
                        
                        
                    else:
                        expressions = []
                        for exp in expression.FalseBody.statements:
                            expressions.append(exp)
                        i = index+1
                        while(i < len(statements)):
                            expressions.append(statements[i])
                            i += 1
                        false_body = self.checkEffectsInteraction(expressions,stateVariablesList,contract,flags_false_body,storageVariable=storage_variables_false_body,protected_state_variables=protected_state_variables_false_body)
                
                if expression.FalseBody == None:
                    if true_body == False:
                        return true_body
                    else:
                        continue
                return true_body and false_body
            if(isinstance(expression,dict) and "expression" in expression and expression.expression.type == "FunctionCall"):
                if self.functionCallHandlerCEI(expression, stateVariablesList,contract,flags,storageVariable=storageVariable,protected_state_variables=protected_state_variables):
                    continue
                
            
            if isinstance(expression, dict) and 'expression' in expression:
                # Unary Operation
                if expression.expression.type == 'UnaryOperation':
                    if expression.expression.subExpression.type == 'Identifier':
                        
                        if expression.expression.subExpression.name not in protected_state_variables and expression.expression.subExpression.name in stateVariablesList:
                            return False
                        
                    if expression.expression.subExpression.type == 'IndexAccess' and expression.expression.subExpression not in protected_state_variables and expression.expression.subExpression.base.name in stateVariablesList:
                    # if expression.expression.left.type == 'IndexAccess' and expression.expression.left.base.name in stateVariablesList:
                        
                        return False
                    if flags["interaction"] == True and (expression.expression.subExpression.type == 'IndexAccess' or expression.expression.subExpression.type == 'Identifier'):
                        if expression.expression.subExpression.type == 'IndexAccess' and (expression.expression.subExpression.base.name in stateVariablesList or expression.expression.subExpression.base.name in storageVariable):
                            flags["interaction"] = False
                        elif expression.expression.subExpression.type == 'Identifier' and (expression.expression.subExpression.name in stateVariablesList or expression.expression.subExpression.name in storageVariable):
                            flags["interaction"] = False
                # Binary Operation
                if expression.expression.type == 'BinaryOperation':
                    if expression.expression.left.type == 'Identifier':
                        
                        if expression.expression.left.name not in protected_state_variables and expression.expression.left.name in stateVariablesList:
                            return False
                        elif isinstance(expression.expression.right,dict) and 'expression' in expression.expression.right:
                            if expression.expression.right.expression.memberName == 'send':
                                if flags["interaction"] == True:
                                    return False
                                protected_state_variables.clear()
                                flags["interaction"] = True
                      
                                continue
                    if expression.expression.left.type == 'IndexAccess' and "name" in expression.expression.left.base and (expression.expression.left not in protected_state_variables and expression.expression.left.base.name in stateVariablesList):
                        
                        return False
                  
                    if flags["interaction"] == True and (expression.expression.left.type == 'IndexAccess' or expression.expression.left.type == 'Identifier'):
                        if expression.expression.left.type == 'IndexAccess' and "name" in expression.expression.left and (expression.expression.left.base.name in stateVariablesList or expression.expression.left.base.name in storageVariable):
                            flags["interaction"] = False
                        elif expression.expression.left.type == 'Identifier' and (expression.expression.left.name in stateVariablesList or expression.expression.left.name in storageVariable):
                            flags["interaction"] = False
                if isinstance(expression, dict) and 'expression' in expression.expression and expression.expression.type == 'FunctionCall':
                    
                    if isinstance(expression.expression.expression,list) and self.ifInteraction(expression.expression.expression[0]):
                        if flags["interaction"] == True:
                            return False
                        protected_state_variables.clear()
                        flags["interaction"] = True
                    if isinstance(expression, dict) and 'type' in expression.expression.expression:
                        if expression.expression.expression.type == 'MemberAccess' and self.ifInteraction(expression.expression.expression):
                            if flags["interaction"] == True:
                                return False
                            protected_state_variables.clear()
                            flags["interaction"] = True
                    
                    if isinstance(expression, dict) and 'name' in expression.expression.expression and expression.expression.expression.type == 'Identifier' and expression.expression.expression.name == 'require':
                        len_first = len(protected_state_variables)
                        self.addProtectedVariables(expression.expression.arguments[0],protected_state_variables, stateVariablesList)
                        len_second = len(protected_state_variables)
                        if (len_first != len_second):
                            flags["check"] = True
                            flags["interaction"] = True
        return  flags["check"] and flags["interaction"]
    def getStateVarValue(self,node, stateVars):
        if node.type == "Identifier" and node.name in stateVars:
            return stateVars[node.name].expression
                            
        else: 
            return node
    def checkReentrancy(self, logger):
        contracts = self.node.contracts
        
        for contract in contracts:
            if len(contracts[contract]._node.baseContracts) != 0:
                for base_contract in contracts[contract]._node.baseContracts:
                    base_name = base_contract.baseName.namePath
                    if base_name not in contracts:
                        for import_file in self.node.imports:
                            found = False
                            if found:
                                break
                            if import_file.symbolAliases == None:
                                continue
                            else:
                                for child in import_file.importedFile.children:
                                    if child.type == "ContractDefinition" and import_file.symbolAliases[child.name] == base_name:
                                        base_name = child.name
                    
                    for function in contracts[base_name].functions:
                        if function not in contracts[contract].functions:
                            contracts[contract].functions[function] = contracts[base_name].functions[function]

                    for modifier in contracts[base_name].modifiers:
                        if modifier not in contracts[contract].modifiers:
                            contracts[contract].modifiers[modifier] = contracts[base_name].modifiers[modifier]

                    for stateVar in contracts[base_name].stateVars:
                        if stateVar not in contracts[contract].stateVars:
                            contracts[contract].stateVars[stateVar] = contracts[base_name].stateVars[stateVar]

            functions = contracts[contract].functions
            
            if hasattr(contracts[contract], 'stateVars'):
                
                stateVariables = contracts[contract].stateVars

            for function in functions.keys():
                if function == "payOut":
                    pprint.pprint(f"Contract: {contract} functions:{function}")
                    pprint.pprint(functions[function]._node.body)
                if functions[function]._node.isConstructor == True:
                    for expression in functions[function]._node.body.statements:
                        if expression.type == "EmitStatement":
                            continue
                        right = self.getStateVarValue(expression.expression.right,contracts[contract].stateVars)
                        if "name" in expression.expression.left:
                            contracts[contract].stateVars[expression.expression.left.name].expression = right
                
                # if not (functions[function]._node.visibility == "public" or functions[function]._node.visibility == "external"):
                #     continue
                next_function = False
                if self.checkKeyword(functions[function]._node):
                    
                    for modifier in functions[function]._node.modifiers:
                        
                        if self.isReentrancyGuard(node=contracts[contract].modifiers[modifier.name]._node,contract=contract,storageVariable=dict(),stateVariablesList=stateVariables) == True:
                            next_function = True
                            break
                    if next_function:
                        continue
                    
                    if self.checkEffectsInteraction(node=functions[function]._node,contract=contract,storageVariable=dict(),stateVariablesList=stateVariables) == False:
                        filePath = None
                        contractFound = False
                        for file in self.node.imports:
                            if contractFound:
                                break
                            for child in file.importedFile.children:
                                if child.type == "ContractDefinition" and child.name == contract:
                                    filePath=file.path
                                    contractFound = True
                                    break
                        
                        logger.logVulnerability(contract_name=contract,function_name=function,vulneralbility=self.vulnerability,fileName=filePath)
