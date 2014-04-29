


<?php
    include_once("menu.php");
    include_once("TaobaoHelper.php");
    include_once("TFTools.php");
    include_once("XmlHelper.php");
    ?>

<div class="column one">
<?php
    $request = NULL;
    if(isset($_GET['SessionKey'])){
        $request = new MFRequest($_GET['SessionKey']);
        $_SESSION['SessionKey']=$_GET['SessionKey'];
    }else{
        $request = new MFRequest($_SESSION['SessionKey']);
    }

    $user_info = $request->userGet();
    echoInTable8($user_info);
    echo "<br/>";
    echoInTable4($request->shopGet($user_info->nick));
    echo "<br/>";
?>
</div>

<div class="column two">
<?php
    
    echo <<<EOT
    <script type="text/javascript">
    <!--
    function submitChoice(){
        document.getElementById('formChoice').submit();
    }
    -->
    </script>
    
EOT;
    
    $radioCheck = array(
                        "onsale"=>"",
                        "inventor"=>"",
                        "all"=>"",
    );
    if(isset($_GET['ShowContent'])){
        $op = $_GET['ShowContent'];
        $radioCheck[$op]="checked";
    }else if(isset($_SESSION['ShowContent'])){
        $op = $_SESSION['ShowContent'];
        $radioCheck[$op]="checked";
    }else{
        $op = "onsale";
        $radioCheck[$op]="checked";
    }
    
    
    echo "<form action='home.php' method='get' id='formChoice'>";
    echo "<input type='radio' name='ShowContent' value='onsale'  onclick='submitChoice()'".$radioCheck['onsale']."/> 仅橱窗";
    echo "<input type='radio' name='ShowContent' value='inventor'  onclick='submitChoice()'".$radioCheck['inventor']."/> 仅仓库";
    echo "<input type='radio' name='ShowContent' value='all'  onclick='submitChoice()'".$radioCheck['all']."/> 全部宝贝";
    echo "</from>";
    
    function getArray($node) {
        $array = false;
        
        if ($node->hasAttributes()) {
            foreach ($node->attributes as $attr) {
                $array[$attr->nodeName] = $attr->nodeValue;
            }
        }
        
        if ($node->hasChildNodes()) {
            if ($node->childNodes->length == 1) {
                $array[$node->firstChild->nodeName] = getArray($node->firstChild);
            } else {
                foreach ($node->childNodes as $childNode) {
                    if ($childNode->nodeType != XML_TEXT_NODE) {
                        $array[$childNode->nodeName][] = getArray($childNode);
                    }
                }
            }
        } else {
            return $node->nodeValue;
        }
        return $array;
    }
    
    switch($op){
        case "onsale":{

            echoInTable5($request->itemsOnsaleGet());
        }break;
        case "inventor":{
            echoInTable7($request->itemsInventorGet());
        }break;
        case "all":{
        	$onsale_xml = $request->itemsOnsaleGet();
            $inventor_xml = $request->itemsInventorGet();
   			 append_simplexml($onsale_xml,$inventor_xml);
			 echoInTable9($onsale_xml);
        }break;
        default:
    }
    
    $_SESSION['ShowContent']=$op;




?>

</div>


<div class="column three">
<?php
    
   
    
    $xml = simplexml_load_file('data.xml');
    $parent_node = XF($xml->xpath("user[nick='sandbox_motherfun']"));
    $parent_id=XF($parent_node->xpath("@id"));

    echo "<hr/><a href='home.php?SessionKey=".$parent_node->sessionkey."'>主店铺".$parent_node->nick."</a>";
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        echo "<hr/><a href='home.php?SessionKey=".$child->sessionkey."'>附属店铺".$child->nick."</a>";
    }
    echo "<hr/>";
    
    
   
  //  $x = $dom2->createElement("edit");
  // 	$dom2->appendChild($x);
//	print_r($dom2);
?>

</div>
<?php
    include("foot.php");
?>