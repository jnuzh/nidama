<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");

    $request = new MFRequest($_SESSION['SessionKey']);
    
    $itemInfo = $request->itemGet($_GET['iid']);
    if(isset($_GET['operation'])){
        $op = $_GET['operation'];
        switch($op){
            case "update":{
                if(isset($_GET['num'])){
                    print_r($request->ItemUpdate($_GET['iid'],$_GET['num']));
                }else{
                    print_r($request->ItemUpdateTitle($_GET['iid'],$_GET['title']));
                }
            }break;
            case "delisting":{
                print_r($request->itemUpdateDelisting($_GET['iid']));
                $url="home.php";
                echo "<script language=\"javascript\">";
                echo "location.href=\"$url\"";
                echo "</script>";
            }break;
            case "listing":{
                print_r($request->itemUpdateListing($_GET['iid'],"".$itemInfo->num));
                $url="home.php";
                echo "<script language=\"javascript\">";
                echo "location.href=\"$url\"";
                echo "</script>";
                
            }break;
            case "delete":{
                print_r($request->itemDelete($_GET['iid']));
                $url="home.php";
                echo "<script language=\"javascript\">";
                echo "location.href=\"$url\"";
                echo "</script>";
            }break;
            default:
                
        }
    }else{
        echo "no operation";
    }
    echo "ok";
    $itemInfo = $request->itemGet($_GET['iid']);
    echoInTable6($itemInfo);
    
    echo "<br/>";
    echo "<table border='1'>";
    echo "<tr class='title'><td align='center' colspan=9><font size=5>修改宝贝信息</font></td></tr>";
    echo "<tr>";
    echo "<td>";
    echo "<form action='ItemUpdate.php' method='get'>";
    echo "<input type='hidden' name='iid' value='".$_GET['iid']."'/>";
    echo "<input type='hidden' name='operation' value='update'/>";
    echo "<br/><br/>数量: <input type='text' name='num' />";
    echo "<input type='submit' value='提交修改'/>";
    echo "</form>";
    echo "</td>";
    echo "</tr>";
    echo "<tr><td>";
    echo "<form action='ItemUpdate.php' method='get'>";
    echo "<input type='hidden' name='iid' value='".$_GET['iid']."'/>";
    echo "<input type='hidden' name='operation' value='update'/>";
    echo "<br/><br/>名称: <input type='text' name='title' />";
    echo "<input type='submit' value='提交修改'/>";
    echo "</form>";
    echo "</td></tr>";
    echo "</table>";

?>



<?php
    include("foot.php");
    ?>