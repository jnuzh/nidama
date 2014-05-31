<?php
    
    
    include_once("TaobaoHelper.php");
    include_once("EchoHelper.php");
    include_once("XmlHelper.php");
    include_once("MsgHelper.php");
    include_once("ajaxPage.php");
    
    $groupid = "A10086";
    $username = "sandbox_motherfun";
    
    $nick = isset($_REQUEST['nick'])?$_REQUEST['nick']:$username;
    
    $all_shops = simplexml_load_file('shops_data.xml');
    $req = new MFRequest(XF($all_shops->xpath("shop[nick='$nick']"))->sessionkey);
    
    $groups = simplexml_load_file('groups_data.xml');
    
    
    $trades = $req->tradesSoldGet();
    if($trades==null) $req->print_error();
    
    $show = isset($_REQUEST['show'])?$_REQUEST['show']:"ALL";
    switch($show){
        case "WAIT_BUYER_PAY":{
            $trade_array = $trades->xpath("trade[status='$show']");
        }break;
        case "WAIT_SELLER_SEND_GOODS":{
            $trade_array = $trades->xpath("trade[status='$show']");
        }break;
        case "WAIT_BUYER_CONFIRM_GOODS":{
            $trade_array = $trades->xpath("trade[status='$show']");
        }break;
        case "ALL":{
            $trade_array = $trades->xpath("trade");
        }break;
        default:
    }
    
    
    
    $content_id = "ajax_page_one";                              //区域的id号，必须修改！
    $url ="tradeShowAjax.php?nick=$nick";                                           //当前php文件名，必须修改！
    $page = isset($_REQUEST['page'])?$_REQUEST['page']:1;
    $total = count($trade_array);//记录总条数
    $number = 10;//每页显示条数
    
    echo "<div id='$content_id'>";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=WAIT_BUYER_PAY')\" ".($show=='WAIT_BUYER_PAY'?'checked':'')."/> 未付款";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=WAIT_SELLER_SEND_GOODS')\" ".($show=='WAIT_SELLER_SEND_GOODS'?'checked':'')."/> 付款待发货";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=WAIT_BUYER_CONFIRM_GOODS')\" ".($show=='WAIT_BUYER_CONFIRM_GOODS'?'checked':'')."/>已发货";
    echo "<input type='radio'  onclick=\"dopage('$content_id','$url&show=ALL')\" ".($show=='ALL'?'checked':'')."/>全部";
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5><font size=5>".$nick."的订单列表</font></font></td></tr>";
    echo "<tr class='titleList'>";
    echo "<td>订单编号</td>";
    echo "<td>创建时间</td>";
    echo "<td>买家昵称</td>";
    echo "<td>支付金额</td>";
    echo "<td>交易状态</td>";
    echo "<td>操作</td>";
    echo "</tr>";
    for($i=0;$i<$number;$i++){
        $index = ($page-1)*$number+$i;
        if($index>=$total) break;
        $child = $trade_array[$index];
        echo "<tr>";
        echo "<td>$child->tid</td>";
        echo "<td>$child->created</td>";
        echo "<td>$child->buyer_nick</td>";
        echo "<td>$child->payment</td>";
        echo "<td>$child->status</td>";
        echo "<td><a href='tradeEditor.php?nick=$nick&tid=$child->tid'>查看</a></td>";
        echo "</tr>";
    }
    echo "</table>";
    echo ajaxPage($content_id,"$url&show=$show",$total,$number);
    
    echo "</div>";
    ?>