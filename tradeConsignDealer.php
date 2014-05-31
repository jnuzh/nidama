<?php
        include("header.php");
    
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    
    
    $user_id = $_REQUEST['user_id'];
    $lcomId = $_REQUEST['lcomId'];
    $tid = $_REQUEST['tid'];
    $username = "sandbox_motherfun";
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    $req = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);
    
    $trade =  $req->tradeFullinfoGet($tid);
    $laddr = $req->logisticsAddressSearch();
    
    
    $result = $req->logisticsConsignOrderCreateandsend($user_id,$lcomId,$tid,$laddr->address_result,$trade);
    print_r($result);
    if($result!=null){
        $url="tradeEditor.php?tid=$tid";
        echo "<script language=\"javascript\">";
        echo "location.href=\"$url\"";
        
        echo "</script>";
    }else{
        echo "发货失败！";
        $req->print_error();
    }
    
    ?>

