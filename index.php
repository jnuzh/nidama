<?php
    include("menu.php");
    
 
    
    if(isset($_GET['SessionKey'])){
        $_SESSION['SessionKey'] =$_GET['SessionKey'];
    }
    
    
    /*
    if("MainShop"!=$_SESSION['Authorize']){
        $url="authorize.php";
        echo "<script language=\"javascript\">";
        echo "location.href=\"$url\"";
        echo "</script>";
    }
     */

    $xml = simplexml_load_file('data.xml');
    foreach ($xml->children() as $child) {
        echo "<br/><a href = 'home.php?SessionKey=".$child->sessionkey."'>".$child->nick."的淘宝店铺</a>";
    }
    
    
/*
    if(isset($_GET['SessionKey'])){
        echo "<br/><a href = 'home.php?sessionKey=".$_SESSION['SessionKey']."'>查看当前sessionKey的淘宝店铺</a>";
    }
*/


    
    
    echo "<br/>";
    echo <<<EOT
    <p>该应用可以用于已有店铺的数据同步，也可以用于新开分销店进行数据复制</p>
EOT;

    include("foot.php");
?>