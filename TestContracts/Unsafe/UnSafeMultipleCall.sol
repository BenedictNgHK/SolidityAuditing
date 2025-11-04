error ReentrancyError();
pragma solidity ^0.8.20;

contract EtherStore  {


    int [10] i ;
    int j;
    mapping(address => uint256) balances;
    
   
    function withdraw()   external{
        
        
        if(balances[msg.sender] == 0)
            revert ReentrancyError();
        
      
        
        balances[msg.sender]--;
        
        msg.sender.call{value: 1}("");
        msg.sender.call{value: 1}("");
        balances[msg.sender]--;

    }
    

    function getBalance()  public view returns (uint256) {
            

        return address(this).balance;
    }
}
