<?php

    
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    include_once("MsgHelper.php");
    include_once("ajaxPage.php");

    $groupid = "A10086";
    $username = "sandbox_motherfun";
    
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $req = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);

    $groups = simplexml_load_file('groups_data.xml');
    
    $op = isset($_REQUEST['op'])?$_REQUEST['op']:"none";
    switch($op){
        case "delisting":{
            $req->itemUpdateDelisting($_REQUEST['num_iid']);
            localMsgConsume("taobao_item_ItemDownshelf",$nick,$_REQUEST['num_iid']);
        }break;
        case "listing":{
            $req->itemUpdateListing($_REQUEST['num_iid'],$_REQUEST['num']);
            localMsgConsume("taobao_item_ItemUpshelf",$nick,$_REQUEST['num_iid']);
        }break;
        case "delete":{
            $req->itemDelete($_REQUEST['num_iid']);
            localMsgConsume("taobao_item_ItemDelete",$nick,$_REQUEST['num_iid']);
        }break;
        case "add":{
            $req->itemAddWithTitle("妖器「御币」");
        }break;
        case "addSerialA":{
            $req->itemsAddWithTitle("天使");
        }break;
        case "addSerialB":{
            $req->itemsAddWithTitle("路人");
        }break;
        case "addSerialC":{
            $req->itemsAddWithTitle("恶魔");
        }break;
        case "deleteAll":{
            $xml = $req->itemsAllGet();
            foreach($xml->item as $item){
                $req->itemDelete($item->num_iid);
            }
        }break;
        default:
    }
    

    $show = isset($_REQUEST['show'])?$_REQUEST['show']:"onsale";
    switch($show){
        case "onsale":{
            $xml = $req->itemsOnsaleGet();
        }break;
        case "instock":{
            $xml = $req->itemsInventorGet();
        }break;
        case "all":{
            $xml = $req->itemsAllGet();
        }break;
            
        default:
    }

    
    $content_id = "ajax_page_one";                              //区域的id号，必须修改！
    $url ="shopItemShow.php?nick=$nick";                                           //当前php文件名，必须修改！
    $page = isset($_REQUEST['page'])?$_REQUEST['page']:1;
    $total = count($xml->item);//记录总条数
    $number = 10;//每页显示条数
    

    echo "<div id='$content_id'>";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=onsale')\" ".($show=='onsale'?'checked':'')."/> 仅橱窗";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=instock')\" ".($show=='instock'?'checked':'')."/>仅仓库";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=all')\" ".($show=='all'?'checked':'')."/> 全部宝贝";
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5>".$nick."的宝贝列表</font></td></tr>";
    echo "<tr class='titleList'>";
    echo "<td>ID</td>";
    echo "<td>名称</td>";
   // echo "<td>图片</td>";
    echo "<td>价格</td>";
    echo "<td>出售状态</td>";
    echo "<td>数量</td>";
    echo "<td>关联组别</td>";
    echo "<td>操作</td>";
    echo "<td>操作</td>";
    echo "<td>操作</td>";
    echo "</tr>";
    for($i=0;$i<$number;$i++){
        $child = $xml->item[($page-1)*$number+$i];
        if($child==null) break;
        echo "<tr>";
        echo "<td>$child->num_iid</td>";
        echo "<td>$child->title</td>";
       // echo "<td><img src='$child->pic_url'></td>";
        echo "<td>$child->price</td>";
        echo $child->approve_status=="onsale"?
        "<td>出售中</td>":
        "<td>在仓库</td>";
        echo "<td>$child->num</td>";
        $tid = $groups->xpath("group[items/item[num_iid='$child->num_iid']]/@id");
        echo "<td>".($tid==null?"未关联":$tid[0])."</td>";
        echo "<td><a href='ItemEditor.php?nick=$nick&num_iid=$child->num_iid'>编辑</a></td>";
        echo $child->approve_status=="onsale"?
        "<td>"."<a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=delisting&num_iid=$child->num_iid');>下架</a>"."</td>":
        "<td>"."<a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=listing&num_iid=$child->num_iid&num=$child->num');>上架</a>"."</td>";
        echo "<td>"."<a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=delete&num_iid=$child->num_iid');>删除</a>"."</td>";
        echo "</tr>";
    }
    echo "</table>";
    echo ajaxPage($content_id,"$url&show=$show",$total,$number);
    
    
    
    echo "<br/><br/><hr/>供开发人员测试使用：";
    echo "<br/><a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=add');>增加一件测试商品</a>";
    echo "<br/><a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=addSerialA');>增加天使系列测试商品</a>";
    echo "<br/><a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=addSerialB');>增加人类系列测试商品</a>";
    echo "<br/><a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=addSerialC');>增加恶魔系列测试商品</a>";
    echo "<br/><a href=javascript:dopage('$content_id','$url&show=$show&page=$page&op=deleteAll');>删除所有商品</a>";
    echo "</div>";
    
    
    
    ?>