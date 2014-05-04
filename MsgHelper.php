<?php
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");

    class MFPrint{
        private $linefeed;
        private $enable;//用于开启关闭输出
        
        function __construct($linefeed){
            $this->linefeed =   $linefeed;
            $this->enable   =   true;
        }
        
        function print_line($str){
            if($this->enable){
                echo $str;
                echo $this->linefeed;
            }
        }
        
        function setEnable($b){
            $this->enable = $b;
        }
    }
    
    function localMsgConsume($topic,$nick,$num_iid){
        $printer = new MFPrint('<br/>');
        $printer->setEnable(false);
        commonMsgConsume($topic,$nick,$num_iid,$printer);
    }
    
    function remoteMsgConsume($topic,$nick,$num_iid){
        $printer = new MFPrint('\n');
        commonMsgConsume($topic,$nick,$num_iid,$printer);
    }
    
    function commonMsgConsume($topic,$nick,$num_iid,$p){
        
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
        
        
        $p->print_line("BEGIN****************消息出现，开始分析！**************** ");
        $p->print_line("这次消息的信息如下：");
        $p->print_line("昵称是：$nick ");
        $p->print_line("商品id是：$num_iid  ");
        $p->print_line("消息主题是：$event_topic ");
        
        /***************   对关联商品进行操作        **************/
        //找到所在的关联小组
        $event_items = XF($groups->xpath("group/items[item[num_iid='$event_num_iid']]"));
        if($event_items==null){
            $p->print_line("****************没有找到关联小组！消息消费完毕****************END ");
            return;
        }else{
            $p->print_line("****************找到关联小组！开始执行！**************** ");
        }

        
        foreach($event_items as $item){
            if((string)$item->num_iid!=(string)$event_num_iid){

                $p->print_line(" 发现一件关联商品！");
                $p->print_line(" 商品id是：$item->num_iid  ");
                $p->print_line("店主是：$item->nick ");
                $req = $request_array[(string)($item->nick)];
                switch($event_topic){
                    case "taobao_item_ItemAdd":{//增加
                        
                    }break;
                    case "taobao_item_ItemDelete":{//删除
                        $result = $req->itemDelete($item->num_iid);
                        if($result) $p->print_line("操作是ItemDelete:对商品 $item->num_iid 进行了删除操作。");
                        else $req->print_error();

                        //确保本地数据的同步
                        $local_item = XF($groups->xpath("group/items/item[num_iid='$item->num_iid']"));
                        $local_item->num_iid=null;
    
                        
                    }break;
                    case "taobao_item_ItemUpdate":{//修改
                        $p->print_line("操作是ItemUpdate:对商品 $item->num_iid 进行了更新操作。");
                    }break;
                    case "taobao_item_ItemUpshelf":{//上架
                        $info = $req->itemGet($num_iid);
                        $result = $req->itemUpdateListing($item->num_iid,$info->num);
                        if($result) $p->print_line("操作是ItemUpshelf:对商品  $item->num_iid  进行了上架操作。");
                        else $req->print_error();
                    }break;
                    case "taobao_item_ItemDownshelf":{//下架
                        $result = $req->itemUpdateDelisting($item->num_iid);
                        if($result) $p->print_line("操作是ItemDownshelf:对商品 $item->num_iid 进行了下架操作。");
                        else $req->print_error();
                    }break;
                    default:{
                        $p->print_line("没有订阅过这种消息：$event_topic ");
                    }
                }
            }
        }
        
        
        
        /***************   对此次消息的目标商品进行操作        **************/
        
        switch($event_topic){
            case "taobao_item_ItemAdd":{//增加
                
            }break;
            case "taobao_item_ItemDelete":{//删除
                //确保本地数据的同步
                $local_item = XF($groups->xpath("group/items/item[num_iid='$event_num_iid']"));
                $local_item->num_iid=null;
                
            }break;
            case "taobao_item_ItemUpdate":{//修改
                
            }break;
            case "taobao_item_ItemUpshelf":{//上架
                
            }break;
            case "taobao_item_ItemDownshelf":{//下架
                
            }break;
            default:{
                $p->print_line("没有订阅过这种消息：$event_topic ");
            }
        }
        
        
        $groups->asXML('groups_data.xml');
        $p->print_line("\n****************完成同步，消息消费完毕！****************END ");
        
    }


?>