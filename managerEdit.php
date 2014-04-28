<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");
    include("XmlHelper.php");
   
    echo "<div class='column two'>";


    $xml = simplexml_load_file('data.xml');
    $parent_node = $xml->xpath("user[nick='sandbox_motherfun']")[0];
    $parent_id=$parent_node->xpath("@id")[0];
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }

    $xml_array=array();
    foreach($request_array as $child){
       
        $tmp1_xml = $child->itemsOnsaleGet();
        $tmp2_xml = $child->itemsInventorGet();
        append_simplexml($tmp1_xml,$tmp2_xml);
        $xml_array[]=$tmp1_xml;
    }
   

    
    echoInTable6($request_array[0]->itemGet($xml_array[0]->item[0]->num_iid.""));
    
    echo <<<EOT
    <script type="text/javascript">
    <!--
    function submitOption(e){
        document.getElementById("iidInShop_"+e.toString()).submit();
    }
    -->
    </script>
EOT;
  
    for($j = 1;$j<count($xml_array);$j++){
        echo "<hr/><form action='managerEdit.php' method='get' name='iidInShop_".$j."' id= 'iidInShop_".$j."'>附属店铺".$j."   <select name='iid' onChange='submitOption(".$j.")'>";
        echo "<option value='".$subChild->num_iid."'>无</option>";
        echo "<option value='".$subChild->num_iid."'>复制主商品</option>";
        foreach($xml_array[$j]->item as $subChild){
            echo "<option value='".$subChild->num_iid."'>".$subChild->title."</option>";
        }
        echo "<input type='hidden' name='shop' value='".$j."'/>";
        echo "</select></form>";
        if(count($xml_array[$j]->item)){
            echoInTable6($request_array[$j]->itemGet($xml_array[$j]->item[0]->num_iid.""));
        }
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
    <li>选择复制商品，将会在附属店铺中添加一个与主店铺商品信息完全一样的商品。</li>
     <li>可以切换主店铺进行复制操作，但是只有真正的主店铺才能进行同步（待定）</li>
    </ul>
    
EOT;
    
    
    echo "</div>";
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    include("foot.php");
    ?>