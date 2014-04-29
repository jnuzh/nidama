<?php

    //显示同步列表
    include_once ("TFPage.php"); //分页类
    @$page=$_GET['page'];
    if(!$page){
        $page = 1;
    }
    $totail = count($syn_xml->item);//记录总条数
    $number = 10;//每页显示条数
    
    $my_page=new PageClass($totail,$number,$page,'?page={page}');
    echo "<table border=1>";
    echo "<tr class='title'><td align='center' colspan=10><font size=5>商品同步状况显示</font></td></tr>";
    echo "<tr class='titleList'>";
    echo "<td>主店铺</td>";
    for($j = 0;$j<count($request_array);$j++){
        if($j==0) continue;
        echo "<td>附属店铺".$j."</td>";
    }
    echo "<td>同步数量</td>";
    echo "<td>操作</td>";
    echo "<td>删除</td>";
    echo "</tr>";
    for($i=0;$i<$number;$i++){
        if($i>=count($syn_xml->chief_item)) break;
        $chief_item = $syn_xml->chief_item[($page-1)*$number+$i];
        echo "<tr>";
        $m = $chief_item->xpath("@iid");
        $n = $xml_array[0]->xpath("item[num_iid=".$m[0]."]");
        echo "<td>".$n[0]->title."</td>";
        for($j = 0;$j<count($request_array);$j++){
            if($j==0) continue;
            $find = $chief_item->xpath("sub_item[nick='".$nick_array[$j]."']");
            if($find!=null){
                $result = $xml_array[$j]->xpath("item[num_iid='".(string)$find[0]->iid."']");
                if($result!=null && $chief_item->sub_item[0]!=null){
                    echo "<td>".$result[0]->title."</td>";
                    continue;
                }
            }
            echo "<td>无</td>";
        }
        echo "<td>".XF($xml_array[0]->xpath("item[num_iid=".XF($chief_item->xpath("@iid"))."]/num"))."</td>";
        echo "<td>"."<a href='managerEdit.php?chief_iid=".XF($chief_item->xpath("@iid"))."'>编辑</a>"."</td>";
        echo "<td>"."<a href='manager.php?operation=delete&iid=".XF($chief_item->xpath("@iid"))."'>删除</a>"."</td>";
        echo "</tr>";
    }
    echo "</table>";


?>