


<?php
    include_once("header.php");
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    
    $groupid = "A10086";
    $username = "sandbox_motherfun";
    
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $request = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);
    
 
    echo "<div class='column one'>";
    $user_info = $request->userGet();
    echoInTable8($user_info);
    echo "<br/>";
    echoInTable4($request->shopGet($user_info->nick));
    echo "<br/>";
    echo "</div>";

  

    
    echo "<div class='column two'>";
    include_once("shopItemShow.php");
    echo "</div>";


    

    echo "<div class='column three'>";
    $target_shop_array = $all_shops->xpath("shop[groups/groupid='$groupid']");
    foreach ($target_shop_array as $shop) {
        echo "<hr/><a href='shopManager.php?nick=$shop->nick'>组别店铺： $shop->nick</a>";
    }

    echo "<hr/>";
    echo "</div>";



    include("footer.php");
?>