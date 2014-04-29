<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");
    include_once("XmlHelper.php");
    ?>



<?php
    
    if(isset($_GET['operation'])){
        $op = $_GET['operation'];
        switch($op){
            case "add":{
                $syn_xml = simplexml_load_file('SynItems.xml');
                $syn_xml->addChild("chief_item","");
                $syn_xml->chief_item[count($syn_xml)-1]->addAttribute("iid",$_GET['iid']);
                $syn_xml->chief_item[count($syn_xml)-1]->addAttribute("nick","sandbox_motherfun");
                $syn_xml->asXML('SynItems.xml');
            }break;
            case "delete":{
                $syn_xml = simplexml_load_file('SynItems.xml');
                for($i=0;$i<count($syn_xml->chief_item);$i++){
                    if((string)$_GET['iid']==XF((string)$syn_xml->chief_item[$i]->xpath("@iid"))){
                        unset($syn_xml->chief_item[$i]);
                    }
                }
                $syn_xml->asXML('SynItems.xml');

            }break;
            default:
        }
    }else{
       // echo "no operation";
    }

    
    
    echo "<div class='column'>";
    

    
    $xml = simplexml_load_file('data.xml');
    $syn_xml = simplexml_load_file('SynItems.xml');
    
    $parent_node = XF($xml->xpath("user[nick='sandbox_motherfun']"));
    $parent_id=XF($parent_node->xpath("@id"));
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }

    //保存所有商店的商品列表以及店主昵称
    $xml_array=array();
    $nick_array=array();
    foreach($request_array as $child){
        $nick_array[] = $child->userGet()->nick;
        $tmp1_xml = $child->itemsOnsaleGet();
        $tmp2_xml = $child->itemsInventorGet();
        append_simplexml($tmp1_xml,$tmp2_xml);
        $xml_array[]=$tmp1_xml;
    }
    
    
    //主商店中未同步商品列表
    echo "<form action='manager.php' method='get'><select name='iid'>";
    foreach($xml_array[0]->item as $subChild){
        if($syn_xml->xpath("chief_item[@iid='".$subChild->num_iid."']")){
            continue;
        }
        echo "<option value='".$subChild->num_iid."'>".$subChild->title."</option>";
    }
    echo "<input type='hidden' name='operation' value='add'/>";
    echo "<input type='submit' value='添加'/>";
    echo "</select></form>";
    
    
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
    //echo $my_page->myde_write1();
    //".$child->sub_iid[$j]."
    
    
    
    echo "</div>";
    
    
    
    ?>






















<?php
    include("foot.php");
    ?>