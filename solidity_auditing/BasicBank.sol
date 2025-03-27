//SPDX-License-Identifier: MIT
pragma solidity 0.7.0;

contract BasicBank {
    mapping(address => uint) private userFunds;
    address private commissionCollector;
    uint private collectedComission = 0;

    constructor() {
        commissionCollector = msg.sender;
    }

    modifier onlyCommissionCollector() {
        require(msg.sender == commissionCollector);
        _;
    }

    function deposit() public payable {
        require(msg.value >= 1 ether);
        userFunds[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) external payable {
        require(getBalance(msg.sender) >= _amount);
        msg.sender.call{value: _amount}("");
        userFunds[msg.sender] -= _amount;
        userFunds[commissionCollector] += _amount / 100;
    }

    function getBalance(address _user) public view returns (uint) {
        return userFunds[_user];
    }

    function getCommissionCollector() public view returns (address) {
        return commissionCollector;
    }

    function transfer(address _userToSend, uint _amount) external {
        userFunds[_userToSend] += _amount;
        userFunds[msg.sender] -= _amount;
    }

    function setCommissionCollector(
        address _newCommissionCollector
    ) external onlyCommissionCollector {
        commissionCollector = _newCommissionCollector;
    }

    function collectCommission() external {
        userFunds[msg.sender] += collectedComission;
        collectedComission = 0;
    }
}
