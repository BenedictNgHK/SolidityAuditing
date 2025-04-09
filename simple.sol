contract Hello {
    function none() public {
        (bool sent, bytes memory val) = msg.sender.call{value:1}("");
    }
}
