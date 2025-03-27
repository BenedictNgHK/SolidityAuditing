// SPDX-License-Identifier: MIT

pragma solidity ^0.8.13;

error NotOwner();
error NotEnoughEther();
error NotEnoughPetrol();
contract PetrolExchange{

    address public owner;
    mapping(address=>uint) petrolBalance;
    mapping (address=>uint) balances;
    constructor (){
        owner = msg.sender;
        petrolBalance[owner] = 10000;

    }
    modifier OnlyOwner(){
        if(msg.sender != owner)
            revert NotOwner();
        _;
    }
    function checkBalance() public view returns (uint){

        return petrolBalance[address(this)];
    }
    function addPetrol(uint amount ) public OnlyOwner {
        petrolBalance[address(this)] += amount;
    }
     function withdraw() external {
        

    if(balances[msg.sender] == 0)
        revert NotEnoughEther();
        
    //    require(balances[msg.sender] > 0);
       
        

        payable (msg.sender).transfer(balances[msg.sender] );
    //     balances[msg.sender] = 0;
        //getBalance();
        // else if(false)
        // {
            
        // }
        // else
        //     balances[msg.sender] = 1;

        
    }
    function buyPetrol(uint amount) public payable{
        if(msg.value < 0.001 ether)
            revert NotEnoughEther();
        if(msg.value > petrolBalance[address(this)])
            revert  NotEnoughPetrol();
        petrolBalance[address(this)] -= amount;
        petrolBalance[msg.sender] +=amount;

    }

}