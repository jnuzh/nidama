<?php
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    include_once("ajaxPage.php");
    

    $username = "sandbox_motherfun";
    
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $req = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);
    
    
    $num_iid = $_REQUEST['num_iid'];
    
    $op = isset($_REQUEST['op'])?$_REQUEST['op']:"none";
    switch($op){
        case "update_num":{
            $req->ItemUpdateNum($_REQUEST['num_iid'],$_REQUEST['num']);
        }break;
        case "update_title":{
            $req->ItemUpdateTitle($_REQUEST['num_iid'],$_REQUEST['title']);
        }break;
        case "update_desc":{
            $req->ItemUpdateDesc($_REQUEST['num_iid'],$_REQUEST['desc']);
        }break;
        default:
    }
    
    $xml = $req->itemGet($num_iid);

    $content_id = "ajax_content_one";                              //区域的id号，必须修改！
    $url ="singleItemShow.php?nick=$nick&num_iid=$num_iid";
    
    echo "<div id='$content_id'>";
    echo "<table border='1'>";
    echo "<tr class='title'><td align='center' colspan=9><font size=5>商品属性</font></td></tr>";
    echo "<tr><td>ID</td><td>".$xml->num_iid."</td></tr>";
    echo "<tr><td>名称</td><td>".$xml->title."</td></tr>";
    echo "<tr><td>描述</td><td>".$xml->desc."</td></tr>";
    echo "<tr><td>商品链接</td><td><a href=".$xml->detail_url.">".$xml->detail_url."</a></td></tr>";
    echo "<tr><td>价格</td><td>".$xml->price."</td></tr>";
    echo "<tr><td>出售状态</td><td>".$xml->approve_status."</td></tr>";
    echo "<tr><td>类别号</td><td>".$xml->cid."</td></tr>";
    echo "<tr><td>数量</td><td>".$xml->num."</td></tr>";
    echo "</table>";
    
    
    
echo <<<EOT
    <script>
    function submitNum(){
        var n =  document.getElementById('num').value;
        dopage('$content_id','$url&op=update_num&num='+n.toString());
    }
    function submitTitle(){
        var n =  document.getElementById('title').value;
        dopage('$content_id','$url&op=update_title&title='+n.toString());
    }
    function submitDesc(){
        var n =  document.getElementById('desc').value;
        dopage('$content_id','$url&op=update_desc&desc='+n.toString());
    }
    function submitBack(){
        window.location.href="shopManager.php?nick=$nick";
    }
    </script>
EOT;
    
    
    
    
    echo "<br/>";
    echo "<table border='1'>";
    echo "<tr class='title'><td align='center' colspan=9><font size=5>修改宝贝信息</font></td></tr>";
    echo "<tr><td>";
    echo "<br/>数量: <input type='text' id='num'/>";
    echo "<input type='submit' value='提交修改' onclick='submitNum()'/>";
    echo "</td></tr>";
    echo "<tr><td>";
    echo "<br/>名称: <input type='text'  id='title' />";
     echo "<input type='submit' value='提交修改' onclick='submitTitle()'/>";
    echo "</td></tr>";
    echo "<tr><td>";
    echo "<br/>描述: <input type='text'  id='desc' />";
    echo "<input type='submit' value='提交修改' onclick='submitDesc()'/>";
    echo "</td></tr>";
    echo "</table>";
    echo "<input type='submit' value='返回' onclick='submitBack()'/>";
    
    echo "</div>";
    

?>