<?php
    include_once("header.php");
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");
    include_once("MsgHelper.php");
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
             echo "收到消息！<br/>";
             
             foreach($resp->messages as $tmc){
                 $msg = $tmc->tmc_message;
                 $event_nick = $msg->nick;
                 $json = $msg->content;
                 $event_num_iid = $json[0]->num_iid;
            
                 localMsgConsume($msg->topic,$event_nick,$event_num_iid);
            }
         }
     }
 
    
    
    include_once("footer.php");


?>