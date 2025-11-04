pragma solidity ^0.4.22;

contract DelegateCallReentrancy {
    mapping(address => uint) public balances;
    address public owner;

    constructor() public {
        owner = msg.sender;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABLE: Delegatecall without proper validation
    function execute(address _contract, bytes _data) public {
        require(msg.sender == owner, "Only owner can execute");

        // State update before delegatecall - but delegatecall can modify storage
        balances[msg.sender] += 1;

        // VULNERABLE: Delegatecall can modify this contract's storage
        _contract.delegatecall(_data);

        // This state update might be affected by the delegatecall
        balances[msg.sender] -= 1;
    }

    // VULNERABLE: Unprotected delegatecall
    function upgrade(address _newImplementation) public {
        require(msg.sender == owner, "Only owner can upgrade");

        // VULNERABLE: Delegatecall with user data
        _newImplementation.delegatecall(msg.data);
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
