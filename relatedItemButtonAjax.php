<?php
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    
    
    $groupid = $_REQUEST['groupid'];
    $items_seq = $_REQUEST['items_seq'];
    $keynick = $_REQUEST['keynick'];
    $json = $_REQUEST['data'];
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");
    
    $groups = simplexml_load_file('groups_data.xml');
    $target_items = XF($groups->xpath("group[@id='$groupid']/items[position()='$items_seq']"));
    
    $target_attributes = $target_items->attributes();
    $target_attributes[0] = $keynick;
    
    $related_items = json_decode($json,true);
    
    foreach($related_items as $related_item){
        $nick = $related_item['nick'];
        $num_iid = $related_item['num_iid'];
        $target = $target_items->xpath("item[nick='$nick']");
        if($target==null){
            $target_items->addChild("item","");
            $target_items->item[count($target_items)-1]->addChild("nick",$nick);
            $target_items->item[count($target_items)-1]->addChild("num_iid",$num_iid);
        }else{
            $target[0]->num_iid = $num_iid;
        }
    }
    $groups->asXML('groups_data.xml');

    
?>
