<?php
    include_once("header.php");
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    include_once("ajaxPage.php");

    

    

    

    $groupid = $_REQUEST['groupid'];
    $items_seq = $_REQUEST['items_seq'];
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");

    $groups = simplexml_load_file('groups_data.xml');
    $target_items = XF($groups->xpath("group[@id='$groupid']/items[position()='$items_seq']"));


    foreach ($target_shop_array as $shop) {
        $nick = (string)($shop->nick);
        $req[$nick] = new MFRequest($shop->sessionkey);
        $all_array[$nick]   = $req[$nick]->itemsOnsaleGet();
        append_simplexml($all_array[$nick],$req[$nick]->itemsInventorGet());
    }
    

    echo "<div class='column two'>";
 
  
    
    $url ="relatedItemTableAjax.php?groupid=$groupid&items_seq=$items_seq";
echo <<<EOT
    <script>

    
    function submitOption(content_id,nick,e){
        dopage(content_id,'$url&nick='+nick+'&num_iid='+e.value);
    }

    function submitButton(arr){
        for(var i=0;i<arr.length;i++){
            var sel = document.getElementById("option_"+arr[i]['nick']);
            arr[i]['num_iid'] = sel.options[sel.selectedIndex].value;
        }
        var sel = document.getElementById("option_keynick");
        var keynick = sel.options[sel.selectedIndex].value;
         dopage_ex('relation_id','relatedItemButtonAjax.php?groupid=$groupid&items_seq=$items_seq&keynick='+keynick+'&data='+JSON.stringify(arr),'relatedManager.php');
        //dopage('relation_id','relatedItemButtonAjax.php?groupid=$groupid&items_seq=$items_seq&keynick='+keynick+'&data='+JSON.stringify(arr));

        
    }
    </script>
EOT;
    
    echo "主店铺卖家昵称：";
    echo " <select id='option_keynick'  >";
    echo "<option value=''>无</option>";
    foreach($target_shop_array as $shop){
        $keynick = XF($target_items->xpath("@keynick"));
        echo "<option value='$shop->nick'  ".((string)($shop->nick)==$keynick?"selected":"").">$shop->nick</option>";
    }
    echo "</select>";
    
    
    foreach($target_shop_array as $shop){
        $nick = (string)($shop->nick);
        $target_item = $target_items->xpath("item[nick='$nick']");
        $target_num_iid = (string)($target_item==null?"":$target_item[0]->num_iid);
        $content_id = "ajax_".$nick;
        
        echo "<hr/>";
        echo "昵称为$nick 的店铺商品：";
        echo " <select id='option_$nick'  onChange=submitOption('$content_id','$nick',this) >";
        echo "<option value=''>无</option>";
        foreach($all_array[$nick]->item as $item){//如果已经存在了这个物品，且不是该小组拥有的话，跳过输出
            if(($groups->xpath("group/items/item[num_iid='$item->num_iid']"))!=null && ((string)($item->num_iid)!=$target_num_iid))  continue;
            echo "<option value='$item->num_iid' ".((string)($item->num_iid)==$target_num_iid?"selected":"").">$item->title</option>";
        }
        echo "</select>";
        
        echo "<div id='$content_id'>";
        if($target_num_iid!=null) echoInTable6($req[$nick]->itemGet($target_num_iid));
        echo "</div>";
    }
    
    foreach($target_shop_array as $shop){
        $nick_array[]=array(
            "nick"=>(string)($shop->nick),
            "num_iid"=>"",
        );
    }
    $data = json_encode($nick_array);
    echo "<hr/><input type='button' value='完成' onclick='submitButton($data)'/>";
    echo "<div id='relation_id'></div>";
    echo "</div>";

    
    
    echo "<div class='column four'>";
    echo <<<EOT
    <h3>注意</h3>
    <ul>
    <li>所有新增同步都是以主店铺的商品为准。</li>
    <li>选择附属店铺下拉框中的商品确认信息</li>
    <li>点击确定同步后，附属店铺中指定的商品的出售状态和数量都会被更新为与当前主店铺商品一样</li>
    <li>选择复制商品，将会在附属店铺中添加一个与主店铺商品信息完全一样的商品。(待定)</li>
     <li>可以切换主店铺进行复制操作，但是只有真正的主店铺才能进行同步（待定）</li>
    </ul>
    
EOT;
    echo "</div>";
    
   
    
    
    include("footer.php");
    ?>