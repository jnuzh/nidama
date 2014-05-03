<?php

    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");

    
    $nick = $_REQUEST['nick'];
    $num_iid = $_REQUEST['num_iid'];
    
    if($num_iid!=null){
        $all_shops = simplexml_load_file('shops_data.xml');
        $shop = XF($all_shops->xpath("shop[nick='$nick']"));
        $req = new MFRequest($shop->sessionkey);
        echoInTable6($req->itemGet($num_iid));
    }
?>