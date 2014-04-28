<?php
    include("menu.php");
    include("TaobaoHelper.php");
    include("TFTools.php");
    include("XmlHelper.php");
    ?>



<?php
    
    if(isset($_GET['operation'])){
        $op = $_GET['operation'];
        switch($op){
            case "add":{
                $syn_xml = simplexml_load_file('SynItems.xml');
                $syn_xml->addChild("item","");
                $syn_xml->item[count($syn_xml)-1]->addAttribute("chief_iid",$_GET['iid']);
                $syn_xml->asXML('SynItems.xml');
            }break;
            case "delete":{
                $syn_xml = simplexml_load_file('SynItems.xml');
                for($i=0;$i<count($syn_xml->item);$i++){
                    if((string)$_GET['iid']==(string)$syn_xml->item[$i]->xpath("@chief_iid")[0]){
                        unset($syn_xml->item[$i]);
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
    $parent_node = $xml->xpath("user[nick='sandbox_motherfun']")[0];
    $parent_id=$parent_node->xpath("@id")[0];
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }

    $xml_array=array();
    foreach($request_array as $child){
        
        $tmp1_xml = $child->itemsOnsaleGet();
        $tmp2_xml = $child->itemsInventorGet();
        append_simplexml($tmp1_xml,$tmp2_xml);
        $xml_array[]=$tmp1_xml;
    }

    
    $syn_xml = simplexml_load_file('SynItems.xml');
    
    

    
    $tmp1_xml = $request_array[0]->itemsOnsaleGet();
    $tmp2_xml = $request_array[0]->itemsInventorGet();
    append_simplexml($tmp1_xml,$tmp2_xml);
    $ns_xml = $tmp1_xml;
    //删除相同的
    for($i=0;$i<count($ns_xml->item);$i++){
        foreach($syn_xml->item as $child){
            $syn_iid = $child->xpath("@chief_iid")[0];

            if((string)$ns_xml->item[$i]->num_iid==(string)$syn_iid){
                unset($ns_xml->item[$i]);
            }
        }
    }
    
    //添加
    echo "<form action='manager.php' method='get'><select name='iid'>";
    foreach($ns_xml->item as $subChild){
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
    echo "<td>数量</td>";
    echo "<td>操作</td>";
    echo "<td>删除</td>";
    echo "</tr>";
    for($i=0;$i<$number;$i++){
       // if($i>=count($syn_xml->item)) break;
        $child = $syn_xml->item[($page-1)*$number+$i];
        echo "<tr>";
        echo "<td>".$xml_array[0]->xpath("item[num_iid=".$child->xpath("@chief_iid")[0]."]")[0]->title."</td>";
        for($j = 0;$j<count($request_array);$j++){
            if($j==0) continue;
            foreach($child->sub_iid as $scChild){
                $find_tmp = $xml_array[$j]->xpath("item[num_iid=".$scChild."]");
                if(count($find_tmp)>0) $find = $find_tmp[0];
                else $find=null;
                if($find!=null) break;
            }
            if($find!=null && $child->sub_iid[0]!=null){
                echo "<td>".$find->title."</td>";
            }else{
                echo "<td></td>";
            }
        }
        echo "<td>".$xml_array[0]->xpath("item[num_iid=".$child->xpath("@chief_iid")[0]."]")[0]->num."</td>";
        echo "<td>"."<a href='managerEdit.php?iid=".$child->xpath("@chief_iid")[0]."'>编辑</a>"."</td>";
        echo "<td>"."<a href='manager.php?operation=delete&iid=".$child->xpath("@chief_iid")[0]."'>删除</a>"."</td>";
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