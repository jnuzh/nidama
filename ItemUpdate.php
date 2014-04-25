<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");

    $request = new MFRequest();
    

    if(isset($_GET['operation'])){
        $op = $_GET['operation'];
        switch($op){
            case "update":{
                print_r($request->ItemUpdate($_GET['iid'],$_GET['num']));
            }break;
            case "delisting":{
                print_r($request->itemUpdateDelisting($_GET['iid']));
            }break;
            default:
                
        }
    }else{
        echo "no operation";
    }
    
    echoInTable6($request->itemGet($_GET['iid']));
    
    echo "<br/>";
    
?>
<form action="ItemUpdate.php" method="get">
<input type="hidden" name="iid" value=<?php echo "'".$_GET['iid']."'";  ?>/>
<input type="hidden" name="operation" value="update"/>
<br/><br/>数量: <input type="text" name="num" />
<input type="submit" value="提交修改"/>
</form>

<form action="ItemUpdate.php" method="get">
<input type="hidden" name="iid" value=<?php echo "'".$_GET['iid']."'";  ?>/>
<input type="hidden" name="operation" value="delisting"/>
<input type="submit" value="下架"/>
</form>




<?php
    include("foot.php");
    ?>