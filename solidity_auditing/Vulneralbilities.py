import pprint
class VulnerabilityPerFile: 
    def __init__(self,filename):
        self.vulneralbilities = {}
        self.filename = filename
    def logVulnerability(self, contract_name, function_name, vulnerability):
       
        if contract_name not in self.vulneralbilities:
            self.vulneralbilities[contract_name] = {}

        # If the function doesn't exist in the contract, add it
        if function_name not in self.vulneralbilities[contract_name]:
            self.vulneralbilities[contract_name][function_name] = []
        
        # Add the vulnerability to the function's list
        self.vulneralbilities[contract_name][function_name].append(vulnerability)

    def getvulneralbilities(self):
        """
        Returns all logged vulneralbilities.

        :return: Dictionary of all logged vulneralbilities.
        """
        return self.vulneralbilities

    def getvulneralbilitiesByContract(self, contract_name):
        """
        Returns all vulneralbilities for a specific contract.

        :param contract_name: Name of the contract to filter by.
        :return: Dictionary of vulneralbilities for the specified contract.
        """
        return self.vulneralbilities.get(contract_name, {})

    def getvulneralbilitiesByFunction(self, contract_name, function_name):
        """
        Returns all vulneralbilities for a specific function in a contract.

        :param contract_name: Name of the contract to filter by.
        :param function_name: Name of the function to filter by.
        :return: List of vulneralbilities for the specified function.
        """
        if contract_name in self.vulneralbilities and function_name in self.vulneralbilities[contract_name]:
            return self.vulneralbilities[contract_name][function_name]
        return []
    def formattedPrint(self):
        if len(self.vulneralbilities) == 0:
            if self.filename.startswith("0x"):
                print(f"In address: {self.filename} contains no Reentrancy vulnerability")

            else:
                print(f"In file: {self.filename} contains no Reentrancy vulnerability")
            return
        for contract in self.vulneralbilities:
            if self.filename.startswith("0x"):
                print(f"In address: {self.filename}:")

            else:
                print(f"In file: {self.filename}:")
            print(f"\tIn contract {contract}:")
            for function in self.vulneralbilities[contract]:
                print(f"\t\tIn function {function}:")
                for vulnerability in self.vulneralbilities[contract][function]:
                    print(f"\t\t\tVulnerability: {vulnerability}")
            
    def clearvulneralbilities(self):
        """
        Clears all logged vulneralbilities.
        """
        self.vulneralbilities = {}
class VulnerabilityLogger:
    def __init__(self,filename):
        
        self.vulneralbilities = []
        self.vulneralbilities.append(VulnerabilityPerFile(filename))
    def formattedPrint(self):
        if len(self.vulneralbilities[0].vulneralbilities) == 0 and len(self.vulneralbilities) == 1:
            if self.vulneralbilities[0].filename.startswith("0x"):
                print(f"In address: {self.vulneralbilities[0].filename} contains no Reentrancy vulnerability")

            else:
                print(f"In file: {self.vulneralbilities[0].filename} contains no Reentrancy vulnerability")
            return
        for vulneralbility in self.vulneralbilities:
            vulneralbility.formattedPrint()
    def logVulnerability(self, contract_name, function_name, vulneralbility,fileName=None):
        if fileName == None:
            fileName = self.vulneralbilities[0].filename
        fileExist = False
        for file in self.vulneralbilities:
            if file.filename == fileName:
                fileExist = True
                vul_per_file = file
                break
        if not fileExist:
            vul_per_file = VulnerabilityPerFile(fileName)
        vul_per_file.logVulnerability(contract_name,function_name,vulneralbility)
        if not fileExist:
            self.vulneralbilities.append(vul_per_file)
        