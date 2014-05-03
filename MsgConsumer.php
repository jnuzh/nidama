<?php
    include_once("header.php");
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");
    date_default_timezone_set('Asia/Shanghai');
    
    $groups = simplexml_load_file('groups_data.xml');
    
    //获取所有的店铺
    $all_shops = simplexml_load_file('shops_data.xml');
    foreach ($all_shops as $shop) {
        $nick = (string)($shop->nick);
        $request_array[$nick] = new MFRequest($shop->sessionkey);
    }
    
    
     set_time_limit(0);
    $n=20;
     while ($n--) {
         sleep(5);
         echo "监听消息中...";
         
         
         
         
         foreach($request_array as $req){
             $resp = $req->tmcMessagesConsume();//收集消息
            // file_put_contents('msg.txt',$resp,FILE_APPEND);//记录消息
             
             
             if(count($resp->messages)==0) continue;
             echo "收到消息！";
             
             foreach($resp->messages as $tmc){
                 $msg = $tmc->tmc_message;
                 //获取这次消息的nick、num_iid【对于暂时添加的消息有用
                 $event_nick = $msg->nick;
                 $json = $msg->content;
                 
                 $event_num_iid = $json[0]->num_iid;
            
              
               
                 
                 //找到所在的关联小组
                 $event_items = $groups->xpath("group/items[item[num_iid='$event_num_iid']]");
                 if($event_items==null) continue;
                 echo "找到关联小组！";
                 foreach($event_items as $item){
                     if((string)$item->num_iid!=(string)$event_num_iid){
                         $req = $request_array[(string)$item->nick];
                         switch($msg->topic){
                             case "taobao_item_ItemAdd":{//增加
                                 
                             }break;
                             case "taobao_item_ItemDelete":{//删除
                                 $req->itemDelete($item->num_iid);
                                 echo "将num_iid号为$item->num_iid的商品进行了删除操作。";
                             }break;
                             case "taobao_item_ItemUpdate":{//修改
                                 echo "";
                             }break;
                             case "taobao_item_ItemUpshelf":{//上架
                                 $info = $req->itemGet($num_iid);
                                 $req->itemUpdateListing($item->num_iid,$info->num);
                                 echo "将num_iid号为$item->num_iid的商品进行了上架操作。";
                             }break;
                             case "taobao_item_ItemDownshelf":{//下架
                                 $req->itemUpdateDelisting($item->num_iid);
                                echo "将num_iid号为$item->num_iid的商品进行了下架操作。";
                             }break;
                             default:{
                                 echo "没有订阅过这种消息：".$msg->topic."";
                             }
                         }
                     }
                 }
             }
         }
         
         
         
         
         
         
         ob_flush();
         flush();
         usleep(1000);
     }
 
    //	print_r($request->itemAdd());//辅助工具，添加商品
    
    include_once("footer.php");


?>