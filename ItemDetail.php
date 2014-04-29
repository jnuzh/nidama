<?php
    
    header('Content-type:text/html;charset=utf-8');
    include("TaobaoHelper.php");
    include("TFTools.php");
    include_once("XmlHelper.php");
    
    $xml = simplexml_load_file('data.xml');
    $parent_node = $xml->xpath("user[nick='sandbox_motherfun']")[0];
    $parent_id=$parent_node->xpath("@id")[0];
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }
    
    
    $iid = $_REQUEST['iid'];
    $shop = $_REQUEST['shop'];
    if($iid!=null) {
        echoInTable6($request_array[$shop]->itemGet($iid));
    }




?>