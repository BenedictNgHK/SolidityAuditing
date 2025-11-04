pragma solidity ^0.4.22;

contract FalsePositive {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // SAFE: External call but no state modifications
    function notify(address _recipient) public {
        // Only external call, no state changes - should NOT be flagged
        _recipient.call(abi.encodeWithSignature("notification()"));
    }

    // SAFE: External call to view function
    function checkBalance(address _token) public view returns (uint) {
        // Staticcall to view function - completely safe
        (bool success, bytes memory data) = _token.staticcall(abi.encodeWithSignature("balanceOf(address)", msg.sender));
        require(success, "Call failed");
        return abi.decode(data, (uint));
    }

    // SAFE: External call after all state changes
    function withdrawAndNotify(uint _amount) public {
        // Checks
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Effects - all state changes first
        balances[msg.sender] -= _amount;
        uint remaining = balances[msg.sender];

        // Interactions - external calls last
        msg.sender.transfer(_amount);

        // Another interaction - but state already updated
        address(0x123).call(abi.encodeWithSignature("logWithdrawal(address,uint256)", msg.sender, _amount));
    }

    // SAFE: Pure function with external call
    function validateAddress(address _addr) public pure returns (bool) {
        // No state modifications possible in pure function
        (bool success,) = _addr.staticcall(abi.encodeWithSignature("isValid()"));
        return success;
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
