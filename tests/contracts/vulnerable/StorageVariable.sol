error ReentrancyError();
pragma solidity ^0.8.20;

contract EtherStore  {


    int [10] i ;
    int j;
    mapping(address => uint256) balances;
    
   
    function withdraw()   external{
        
        int [10] storage store = i;
        require(balances[msg.sender] > 0);

        balances[msg.sender]--;
       
        msg.sender.call{value: 1}("");
   
        store[0]++;
       

    }
    

    function getBalance()  public view returns (uint256) {
            

        return address(this).balance;
    }
}



