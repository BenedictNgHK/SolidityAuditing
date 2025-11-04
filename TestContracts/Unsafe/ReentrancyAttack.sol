pragma solidity ^0.4.22;

contract ReentrancyAttack {
    mapping(address => uint) public balances;
    bool internal locked;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABLE: External call before state update
    function withdraw(uint _amount) public {
        if(balances[msg.sender] >= _amount) {
            // External call first - VULNERABLE
            msg.sender.call.value(_amount)();
            // State update after - allows reentrancy
            balances[msg.sender] -= _amount;
        }
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
