//SPDX-Licneser: MIT
contract test{
    address addr = msg.sender;
    function deposit() public{
      (bool success,) = payable (addr.call).value(1)("");
    }
}