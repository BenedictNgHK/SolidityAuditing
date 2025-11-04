pragma solidity ^0.4.22;

contract SafeBank {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        if(balances[msg.sender] >= _amount) {
            balances[msg.sender] -= _amount;
            msg.sender.call.value(_amount)();
        }
    }
}
