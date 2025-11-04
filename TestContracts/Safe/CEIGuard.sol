pragma solidity ^0.4.22;

contract CEIGuard {
    mapping(address => uint) public balances;
    bool private locked;

    modifier noReentrancy() {
        require(!locked, "Reentrancy detected");
        locked = true;
        _;
        locked = false;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // SAFE: Proper CEI pattern with reentrancy guard
    function withdraw(uint _amount) public noReentrancy {
        // Checks
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Effects
        balances[msg.sender] -= _amount;

        // Interactions
        msg.sender.transfer(_amount);
    }

    // SAFE: Using transfer() instead of call()
    function safeWithdraw(uint _amount) public {
        // Checks
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Effects
        balances[msg.sender] -= _amount;

        // Interactions - transfer has gas limit, safer than call
        msg.sender.transfer(_amount);
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
