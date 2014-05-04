<?php
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");

    function localMsgConsume($topic,$nick,$num_iid){
    
        $groups = simplexml_load_file('groups_data.xml');
        
        //获取所有的店铺
        $all_shops = simplexml_load_file('shops_data.xml');
        foreach ($all_shops as $shop) {
            $nick = (string)($shop->nick);
            $request_array[$nick] = new MFRequest($shop->sessionkey);
        }
        
        $event_nick = $nick;
        $event_num_iid = $num_iid;
        $event_topic = $topic;
        
     
        
        //找到所在的关联小组
        $event_items = XF($groups->xpath("group/items[item[num_iid='$event_num_iid']]"));
        if($event_items==null){
            echo "BEGIN****************没有找到关联小组！消息消费完毕****************END<br/>";
            return;
        }else{
            echo "BEGIN****************找到关联小组！开始执行！****************<br/>";
        }
        
        foreach($event_items as $item){
            if((string)$item->num_iid!=(string)$event_num_iid){
                echo " <hr/>";
                echo " 发现一件关联商品！<br/>";
                echo " 商品id是：$item->num_iid  <br/>";
                echo  "店主是：$item->nick <br/>";
                $req = $request_array[(string)($item->nick)];
                switch($event_topic){
                    case "taobao_item_ItemAdd":{//增加
                        
                    }break;
                    case "taobao_item_ItemDelete":{//删除
                        $result = $req->itemDelete($item->num_iid);
                        if($result) echo "操作是ItemDelete:对商品 $item->num_iid 进行了删除操作。<br/>";
                        else $req->print_error();
                    }break;
                    case "taobao_item_ItemUpdate":{//修改
                        echo "操作是ItemUpdate:对商品 $item->num_iid 进行了更新操作。<br/>";
                    }break;
                    case "taobao_item_ItemUpshelf":{//上架
                        $info = $req->itemGet($num_iid);
                        $result = $req->itemUpdateListing($item->num_iid,$info->num);
                        if($result) echo "操作是ItemUpshelf:对商品  $item->num_iid  进行了上架操作。<br/>";
                        else $req->print_error();
                    }break;
                    case "taobao_item_ItemDownshelf":{//下架
                        $result = $req->itemUpdateDelisting($item->num_iid);
                        if($result) echo "操作是ItemDownshelf:对商品 $item->num_iid 进行了下架操作。<br/>";
                        else $req->print_error();
                    }break;
                    default:{
                        echo "没有订阅过这种消息：$event_topic <br/>";
                    }
                }
            }
        }
        echo "<hr/>****************完成同步，消息消费完毕！****************END<br/>";
        
        
    }
    


?>