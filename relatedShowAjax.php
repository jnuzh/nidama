<?php
    
    
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    include_once("ajaxPage.php");
    
    
    $groupid = "A10086";
    $username="sandbox_motherfun";
    
    //初始化请求对象和商品列表
    $all_shops = simplexml_load_file('shops_data.xml');
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");
    foreach ($target_shop_array as $shop) {
        $req = new MFRequest($shop->sessionkey);
        $all_array[(string)($shop->nick)]   = $req->itemsOnsaleGet();
        append_simplexml($all_array[(string)($shop->nick)],$req->itemsInventorGet());
    }
    
    

    $op = isset($_REQUEST['op'])?$_REQUEST['op']:"none";
    $keynick = isset($_REQUEST['keynick'])?$_REQUEST['keynick']:$username;
    switch($op){
            
        case "add":{
            $groups = simplexml_load_file('groups_data.xml');
            $target_group = XF($groups->xpath("group[@id='$groupid']"));
            $target_group->addChild("items","");
            $newItems = XF($target_group->xpath("items[last()]"));
            $newItems->addAttribute("keynick", $keynick);
            foreach ($target_shop_array as $shop) {
                $newItems->addChild("item","");
                $newItems->item[count($newItems)-1]->addChild("nick",$shop->nick);
                $newItems->item[count($newItems)-1]->addChild("num_iid","");
            }
            $groups->asXML('groups_data.xml');
        }break;
        case "delete":{
            $items_seq = $_REQUEST['items_seq'];
            $groups = simplexml_load_file('groups_data.xml');
            $target_group = XF($groups->xpath("group[@id='$groupid']"));
            unset($target_group->items[intval($items_seq-1)]);
            $groups->asXML('groups_data.xml');
        }break;
        default:
    }


    
    $groups = simplexml_load_file('groups_data.xml');
    $target_items_array = $groups->xpath("group[@id='$groupid']/items");
    
    
    
    $content_id = "ajax_page_one";                              //区域的id号，必须修改！
    $url ="relatedShowAjax.php?groupid=$groupid";                     //当前php文件名，必须修改！
    $page = isset($_REQUEST['page'])?$_REQUEST['page']:1;
    $total = count($target_items_array);//记录总条数
    $number = 20;//每页显示条数

    
    
    echo <<<EOT
    <script>
    function submitAdd(){
        var sel = document.getElementById("option_keynick");
        var keynick = sel.options[sel.selectedIndex].value;
        dopage('$content_id','$url&op=add&keynick='+keynick);
        
    }
    </script>
EOT;
    
    
    echo "<div id='$content_id'>";

    
   //主店铺中未进行关联的商品
    
    echo "默认主店铺：";
    echo " <select id='option_keynick'  >";
    echo "<option value=''>无</option>";
    foreach($target_shop_array as $shop){
        echo "<option value='$shop->nick'  ".((string)($shop->nick)==$keynick?"selected":"").">$shop->nick</option>";
    }
    echo "</select>";
    echo "<input type='submit' value='新增关联小组' onclick='submitAdd()'/>";
    echo "<hr/>";
    
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5>关联商品列表</font></td></tr>";
    echo "<tr class='titleList'>";
    echo "<td>序号</td>";
    foreach($target_shop_array as $shop){
        echo "<td>$shop->nick</td>";
    }
    echo "<td>主店铺</td>";
    echo "<td>操作</td>";
    echo "<td>删除</td>";
    echo "</tr>";
    for($i=0;$i<$number &&(($page-1)*$number+$i)<$total;$i++){
        $target_items = $target_items_array[($page-1)*$number+$i];
        $items_seq = $i+1;
        echo "<tr>";
        echo "<td>$items_seq</td>";
        foreach($target_shop_array as $shop){
            $item = $target_items->xpath("item[nick='$shop->nick']");
            if($item==null){
                echo "<td>无</td>";
            }else{
                $num_iid = $item[0]->num_iid;
                $info = $all_array[(string)($shop->nick)]->xpath("item[num_iid='$num_iid']");
                if($info==null){
                    echo "<td>无</td>";
                }else{
                    $title = $info[0]->title;
                    echo "<td>$title</td>";
                }
            }
        }
        $keynick =  XF($target_items->xpath("@keynick"));
        echo "<td>$keynick</td>";
        echo "<td>"."<a href='relatedItemEditor.php?groupid=$groupid&items_seq=$items_seq'>编辑</a>"."</td>";
        echo "<td>"."<a href=javascript:dopage('$content_id','$url&op=delete&items_seq=$items_seq');>删除</a>"."</td>";
        echo "</tr>";
    }

    echo "</table>";
    echo ajaxPage($content_id,"$url",$total,$number);
    echo "</div>";
   
    
    
    
    ?>