<?PHP
    include_once("header.php");
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");
    include_once("EchoHelper.php");

    $groupid = "A10086";
    $username = "sandbox_motherfun";
    $all_shops = simplexml_load_file('shops_data.xml');
    $show = "onsale";
    $content_id = 23;
    $url = 22;
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    $req = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);
    
    $tid = $_REQUEST['tid'];
    
    $user = $req->userGet();
    $trade =  $req->tradeFullinfoGet($tid);
    $laddr = $req->logisticsAddressSearch();
    $lcom = $req->logisticsCompaniesGet();
    
    
    echoInTable35($trade);
    echoInTable34($trade);
    echo "<hr/>";
  
    echo "<div class='column send'>";
    
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5>收件人信息</font></td></tr>";
    echo "<tr><td>名称</td><td>".$trade->receiver_name."</td></tr>";
    echo "<tr><td>省</td><td>".$trade->receiver_state."</td></tr>";
    echo "<tr><td>市</td><td>".$trade->receiver_city."</td></tr>";
    echo "<tr><td>区</td><td>".$trade->receiver_district."</td></tr>";
    echo "<tr><td>街道</td><td>".$trade->receiver_address."</td></tr>";
    echo "<tr><td>手机号码</td><td>".$trade->receiver_mobile."</td></tr>";
    echo "<tr><td>电话号码</td><td>".$trade->receiver_phone."</td></tr>";
    echo "<tr><td>邮编</td><td>".$trade->receiver_zip."</td></tr>";
    
    echo "</table>";
    echo "</div>";
    echo "<div class='column receive'>";
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5>发货人信息</font></td></tr>";
    echo "<tr><td>名称</td><td>".$laddr->address_result->contact_name."</td></tr>";
    echo "<tr><td>省</td><td>".$laddr->address_result->province."</td></tr>";
    echo "<tr><td>市</td><td>".$laddr->address_result->city."</td></tr>";
    echo "<tr><td>区</td><td>".$laddr->address_result->country."</td></tr>";
    echo "<tr><td>街道</td><td>".$laddr->address_result->addr."</td></tr>";
    echo "<tr><td>手机号码</td><td>".$laddr->address_result->mobile_phone."</td></tr>";
    echo "<tr><td>电话号码</td><td>".$laddr->address_result->receiver_phone."</td></tr>";
    echo "<tr><td>邮编</td><td>".$laddr->address_result->zip_code."</td></tr>";
    echo "</table>";
    
    echo "</div>";
    
    echo "<div class='row'>";

    if($trade->status == "WAIT_SELLER_SEND_GOODS"){
        echo "<form action='tradeConsignDealer.php' method='get'/>";
        echo " 物流公司：<select name='lcomId'  >";
        echo "<option value=''>未选择</option>";
        foreach($lcom->logistics_company as $child){
            echo "<option value='$child->id' >$child->name</option>";
        }
        echo "</select>";
        echo "<input type='hidden' name='user_id' value='$user->user_id'/>";
        echo "<input type='hidden' name='tid' value='$tid'/>";
        echo "<input type='submit' value='立即发货'/>";
        echo "</form>";
    }else{
        echo "已发货";
    }
    

    
    echo "</div>";
    
    include_once("footer.php");
    echo "<hr/>";

    
?>