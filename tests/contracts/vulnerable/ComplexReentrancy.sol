pragma solidity ^0.4.22;

contract ComplexReentrancy {
    mapping(address => uint) public balances;
    mapping(address => bool) public claimedBonus;

    // VULNERABLE: Multiple external calls with state updates
    function claimBonus() public {
        if(!claimedBonus[msg.sender]) {
            claimedBonus[msg.sender] = true;
            // First external call - potentially vulnerable
            msg.sender.call.value(1 ether)();

            // State update happens but another call follows
            balances[msg.sender] += 100;

            // Second external call - definitely vulnerable
            msg.sender.call.value(0.1 ether)();
        }
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABLE: Cross-function reentrancy
    function transferAndCall(address _to, uint _amount) public {
        if(balances[msg.sender] >= _amount) {
            balances[msg.sender] -= _amount;
            // External call that could trigger other functions
            _to.call.value(_amount)();
            // No reentrancy guard
        }
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
