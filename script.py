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
                    if expression.TrueBody.type == "RevertStatement":
                        len_first = len(protected_state_variables)
                        self.addProtectedVariables(expression.condition,protected_state_variables, stateVariablesList)
                        len_second = len(protected_state_variables)
                        if (len_first != len_second):
                            flags["check"] = True
                            flags["interaction"] = True
                        continue
                    if "expression" in expression.TrueBody:
                        expressions = [expression.TrueBody.expression]
                    else:
                        expressions = []
                        revert_invoked = False
                        for exp in expression.TrueBody.statements:
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
                