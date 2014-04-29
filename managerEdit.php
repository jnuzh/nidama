<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");
    include_once("XmlHelper.php");
    
    echo <<<EOT
    <script type="text/javascript">
    <!--
    
    
    function submitOption(e,shopId){
        var xmlhttp;
        if (window.XMLHttpRequest)
        {// code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp=new XMLHttpRequest();
        }
        else
        {// code for IE6, IE5
            xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange=function()
        {
            if (xmlhttp.readyState==4 && xmlhttp.status==200)
            {
                document.getElementById("shop_"+shopId).innerHTML=xmlhttp.responseText;
            }
        }
        var url = "ItemDetail.php?iid="+e.value+"&shop="+shopId;
        xmlhttp.open("POST",url,true);
        xmlhttp.send();
    }
    -->
    </script>
EOT;
    
    
    
    
    
    echo "<div class='column two'>";

    //初始化所有商店的请求对象
    $xml = simplexml_load_file('data.xml');
    $parent_node = $xml->xpath("user[nick='sandbox_motherfun']")[0];
    $parent_id=$parent_node->xpath("@id")[0];
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }

    
    
    //保存所有商店的商品列表以及店主昵称
    $xml_array=array();
    $nick_array=array();
    foreach($request_array as $child){
        $nick_array[] = $child->userGet()->nick;
        $tmp1_xml = $child->itemsOnsaleGet();
        $tmp2_xml = $child->itemsInventorGet();
        append_simplexml($tmp1_xml,$tmp2_xml);
        $xml_array[]=$tmp1_xml;
    }
   
    //先显示主商店的商品
    $chief_iid = $_REQUEST['chief_iid'];
    echoInTable6($request_array[0]->itemGet($chief_iid));


    //显示各个附属商店的商品列表，以及对应的同步商品
    for($j = 1;$j<count($xml_array);$j++){
        echo "<hr/><form action='managerEdit.php' method='get' name='iidInShop_".$j."' id= 'iidInShop_".$j."'>附属店铺".$j."   <select name='iid' onChange='submitOption(this,".$j.")'>";
        echo "<option value=''>无</option>";
        foreach($xml_array[$j]->item as $subChild){
            echo "<option value='".$subChild->num_iid."'>".$subChild->title."</option>";
        }
        echo "<input type='hidden' name='shop' value='".$j."'/>";
        echo "</select></form>";
        
        echo "<div id='shop_".$j."'>";
        if(count($xml_array[$j]->item)){
           $syn_xml = simplexml_load_file('SynItems.xml');
            $chief_item = $syn_xml->xpath("chief_item[@iid=".$chief_iid."]")[0];
            $find = $chief_item->xpath("sub_item[nick='".$nick_array[$j]."']");
            if($find!=null){
                echoInTable6($request_array[$j]->itemGet((string)$find[0]->iid));
            }
            
        }
        echo "</div>";
    }
    echo "<hr/>";
    
    
    
    
    
    echo "<input type='submit' value='同步'/>";
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
    
   
    
    
    include("foot.php");
    ?>