pragma solidity ^0.4.22;

contract IndirectReentrancy {
    mapping(address => uint) public balances;
    mapping(address => bool) public processed;

    // Helper contract interface
    ContractHelper public helper;

    constructor(address _helper) public {
        helper = ContractHelper(_helper);
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABLE: Indirect reentrancy through helper contract
    function processPayment() public {
        if(!processed[msg.sender]) {
            processed[msg.sender] = true;

            // External call to helper - helper can call back
            helper.process(msg.sender);

            // State update after external call
            balances[msg.sender] += 10;
        }
    }

    // VULNERABLE: Function callable by helper
    function callback(uint _amount) public {
        // This can be called reentrantly through the helper
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        msg.sender.call.value(_amount)();
        balances[msg.sender] -= _amount;
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}

contract ContractHelper {
    IndirectReentrancy public mainContract;

    constructor(address _main) public {
        mainContract = IndirectReentrancy(_main);
    }

    function process(address _user) public {
        // This can trigger reentrancy back to main contract
        mainContract.callback(1 ether);
    }
}
