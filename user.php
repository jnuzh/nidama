<?php
    include("header.php");
    
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    
    $groupid = "A10086";
    $all_shops = simplexml_load_file('shops_data.xml');
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");
    
    foreach ($target_shop_array as $shop) {
        $req = new MFRequest($shop->sessionkey);
        $req->tmcUserPermit();
    }

    
    
    echo "<div class='column four'>";
    
    echo "<h2>您当前的组别号为：$groupid</h2>";
    
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=9><font size=5>关联店铺</font></td></tr>";
    echo "<tr>";
    echo "<td>序号</td>";
    echo "<td>店铺卖家昵称</td>";
    echo "<td>操作</td>";
    echo "</tr>";
    foreach($target_shop_array as $shop){
        static $i=0;
        echo "<tr>";
        echo "<td>".++$i."</td>";
        echo "<td>$shop->nick</td>";
        echo "<td>".($i==1?"":"删除")."</td>";
        echo "</tr>";
        
    }
    echo "</table>";
    
    echo "</div>";
    
   
    
    
    
    
    
    
    
    
    
    
    
    
    include("footer.php");
?>