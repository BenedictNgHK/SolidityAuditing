// import "./ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol" ;

error ReentrancyError();
pragma solidity ^0.8.20;

contract EtherStore  is ReentrancyGuard{
    modifier simpleGuard(){
        if(j == 1)
            revert ReentrancyError();
        j = 1;
        _;
        j = 0;
    }

    int j;
    mapping(address => uint256) balances;
    
   
    function withdraw() nonReentrant external{
        
        
        require(balances[msg.sender] > 0);
        
      
        
        
       
        msg.sender.call{value: 1}("");
   
        balances[msg.sender]--;
        
    }
    

    function getBalance()  public view returns (uint256) {
            

        return address(this).balance;
    }
}



