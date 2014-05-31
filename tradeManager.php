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
    
    
    echo "<div class='column one'>";
    $user_info = $req->userGet();
    //echoInTable8($user_info);
    echo "<br/>";
    echoInTable4($req->shopGet($user_info->nick));
    echo "<br/>";
    echo "</div>";
    
    
    echo "<div class='column two'>";
    include("tradeShowAjax.php");
    echo "</div>";

    
    echo "<div class='column three'>";
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");
    foreach ($target_shop_array as $shop) {
        echo "<hr/><a href='tradeManager.php?nick=$shop->nick'>组别店铺： $shop->nick</a>";
    }
    
    
    
    
    echo "</div>";
    
    
    
    include_once("footer.php");
?>