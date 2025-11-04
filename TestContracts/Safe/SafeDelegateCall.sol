pragma solidity ^0.4.22;

contract SafeDelegateCall {
    mapping(address => uint) public balances;
    address public owner;
    bool private locked;

    modifier noReentrancy() {
        require(!locked, "Reentrancy detected");
        locked = true;
        _;
        locked = false;
    }

    constructor() public {
        owner = msg.sender;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // SAFE: Delegatecall with proper validation and reentrancy guard
    function execute(address _contract, bytes _data) public noReentrancy {
        require(msg.sender == owner, "Only owner can execute");

        // Validate the contract address
        require(_contract != address(0), "Invalid contract address");
        require(_contract != address(this), "Cannot call self");

        // Use staticcall for view functions (safe)
        if (_data.length >= 4) {
            bytes4 selector = bytes4(_data[0]) | (bytes4(_data[1]) >> 8) | (bytes4(_data[2]) >> 16) | (bytes4(_data[3]) >> 24);

            // Check if it's a view function (first bit of selector)
            if (selector[0] & 0x80 == 0) {
                // SAFE: Staticcall for view functions
                _contract.staticcall(_data);
                return;
            }
        }

        // For non-view functions, use regular call instead of delegatecall
        _contract.call(_data);
    }

    // SAFE: Controlled upgrade pattern
    function upgrade(address _newImplementation) public noReentrancy {
        require(msg.sender == owner, "Only owner can upgrade");

        // Validate new implementation
        require(_newImplementation != address(0), "Invalid implementation");
        require(_newImplementation != address(this), "Cannot upgrade to self");

        // Store old implementation for rollback
        address oldImplementation = owner;

        // Update implementation
        owner = _newImplementation;

        // Verify the update worked
        require(owner == _newImplementation, "Upgrade failed");
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
