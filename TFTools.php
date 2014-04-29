<html> 
<head> 
<style type="text/css"> 
img { 
width: 80px; //控制图片的宽度 
heigth: 80px; //控制图片的高度 
} 
td{
width:"50"; 
height:"30";
font-size:12px;
color:#000099;
}

tr.title{
border:1px;
height:"30";
colspan:"4";
align="center";
color:#181e1f;
font-size:14;
background:#bde6ea;
}

tr.titleList{
border:1px;
height:"30";
colspan:"4";
    align="center";
color:#181e1f;
    font-size:14;
background:#e4bb6d;
}

td.title{
width:"50";
height:"30";
font-size:12px;
color:#181e1f;

}
tr{
background:#FFFFCC;
}
</style> 
</head> 
<body> 

</body> 
</html>
<?php
    function echoInTable1($xml)
    {
        echo "<table border='1'>";
        foreach ($xml->children() as $child) {
            echo "<tr>";
            echo "<td>" . $child->getName() . "</td>";
            echo "<td>" . $child . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    }
    function echoInTable2($xml)
    {
        echo "<table border='1'>";
        $top = XF($xml->children());
        echo "<tr>";
        foreach ($top->children() as $child) {
            echo "<td>" . $child->getName() . "</td>";
        }
        echo "</tr>";
        foreach ($xml->children() as $child) {
            echo "<tr>";
            foreach ($child->children() as $info) {
                echo "<td>" . $info . "</td>";
            }
            echo "</tr>";
        }
        echo "</table>";
    }

    function echoInTable3($xml)
    {
        
        echo "<table border=1>";
        echo "<tr class='title'>";
            echo "<td>ID</td>";
            echo "<td>名称</td>";
            echo "<td>图片</td>";
            echo "<td>价格</td>";
            echo "<td>出售状态</td>";
            echo "<td>cid</td>";
            echo "<td>数量</td>";
            
        echo "</tr>";
        foreach ($xml->children() as $child) {
            echo "<tr>";
            echo "<td>".$child->num_iid."</td>";
            echo "<td>".$child->title."</td>";
            echo "<td><img src='".$child->pic_url."'></td>";
            echo "<td>".$child->price."</td>";
            echo "<td>".$child->approve_status."</td>";
            echo "<td>".$child->cid."</td>";
            echo "<td>".$child->num."</td>";
            
            echo "</tr>";
        }
        echo "</table>";

    }
    
    function echoInTable4($xml)
    {
        echo "<table border='1'>";
        echo "<tr class='title'><td align='center' colspan=9><font size=5>店铺信息</font></td></tr>";
        echo "<tr><td>cid</td><td>".$xml->cid."</td></tr>";
        echo "<tr><td>sid</td><td>".$xml->sid."</td></tr>";
        echo "<tr><td>店名</td><td>".$xml->title."</td></tr>";
        echo "<tr><td>描述</td><td>".$xml->desc."</td></tr>";
        echo "<tr><td>公告</td><td>".$xml->bulletin."</td></tr>";
        echo "<tr><td>图片</td><td>".$xml->pic_path."</td></tr>";
        echo "<tr><td>卖家昵称</td><td>".$xml->nick."</td></tr>";
        echo "</table>";
    }
   
    function echoInTable6($xml)
    {
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
    }
    function echoInTable5($xml)
    {
 
        include_once ("TFPage.php"); //分页类
        @$page=$_GET['page'];
        if(!$page){
            $page = 1;
        }
        $totail = count($xml->item);//记录总条数
        $number = 5;//每页显示条数
        
        $my_page=new PageClass($totail,$number,$page,'?page={page}');
        echo "<table border=1>";
        echo "<tr class='title'><td align='center' colspan=10><font size=5>橱窗宝贝列表</font></td></tr>";
        echo "<tr class='titleList'>";
        echo "<td>ID</td>";
        echo "<td>名称</td>";
        echo "<td>图片</td>";
        echo "<td>价格</td>";
        echo "<td>出售状态</td>";
        echo "<td>cid</td>";
        echo "<td>数量</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "</tr>";
        for($i=0;$i<$number;$i++){
            $child = $xml->item[($page-1)*$number+$i+1];
            if($child==null) break;
            echo "<tr>";
            echo "<td>".$child->num_iid."</td>";
            echo "<td>".$child->title."</td>";
            echo "<td><img src='".$child->pic_url."'></td>";
            echo "<td>".$child->price."</td>";
            echo "<td>".$child->approve_status."</td>";
            echo "<td>".$child->cid."</td>";
            echo "<td>".$child->num."</td>";
            echo "<td><a href='ItemUpdate.php?iid=$child->num_iid'>编辑</a></td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=delisting'>下架</a>"."</td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=delete'>删除</a>"."</td>";
            echo "</tr>";
        }
        echo "</table>";
        echo $my_page->myde_write1();
        
        if(isset($_POST['update'])){
            echo $_POST['update'];
        }

    }

    function echoInTable7($xml)
    {
        
        include_once ("TFPage.php"); //分页类
        @$page=$_GET['page'];
        if(!$page){
            $page = 1;
        }
        $totail = count($xml->item);//记录总条数
        $number = 5;//每页显示条数
        
        $my_page=new PageClass($totail,$number,$page,'?page={page}');
        echo "<table border=1>";
        echo "<tr class='title'><td align='center' colspan=10><font size=5>仓库宝贝列表</font></td></tr>";
        echo "<tr class='titleList'>";
        echo "<td>ID</td>";
        echo "<td>名称</td>";
        echo "<td>图片</td>";
        echo "<td>价格</td>";
        echo "<td>出售状态</td>";
        echo "<td>cid</td>";
        echo "<td>数量</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "</tr>";
        for($i=0;$i<$number;$i++){
            $child = $xml->item[($page-1)*$number+$i+1];
            if($child==null) break;
            echo "<tr>";
            echo "<td>".$child->num_iid."</td>";
            echo "<td>".$child->title."</td>";
            echo "<td><img src='".$child->pic_url."'></td>";
            echo "<td>".$child->price."</td>";
            echo "<td>".$child->approve_status."</td>";
            echo "<td>".$child->cid."</td>";
            echo "<td>".$child->num."</td>";
            echo "<td><a href='ItemUpdate.php?iid=$child->num_iid'>编辑</a></td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=listing'>上架</a>"."</td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=delete'>删除</a>"."</td>";
            
            echo "</tr>";
        }
        echo "</table>";
        echo $my_page->myde_write1();
        
        if(isset($_POST['update'])){
            echo $_POST['update'];
        }
        
    }

    function echoInTable9($xml)
    {
        
        include_once ("TFPage.php"); //分页类
        @$page=$_GET['page'];
        if(!$page){
            $page = 1;
        }
        $totail = count($xml->item);//记录总条数
        $number = 5;//每页显示条数
        
        $my_page=new PageClass($totail,$number,$page,'?page={page}');
        echo "<table border=1>";
        echo "<tr class='title'><td align='center' colspan=10><font size=5>全部宝贝列表</font></td></tr>";
        echo "<tr class='titleList'>";
        echo "<td>ID</td>";
        echo "<td>名称</td>";
        echo "<td>图片</td>";
        echo "<td>价格</td>";
        echo "<td>出售状态</td>";
        echo "<td>cid</td>";
        echo "<td>数量</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "<td>操作</td>";
        echo "</tr>";
        for($i=0;$i<$number;$i++){
            $child = $xml->item[($page-1)*$number+$i+1];
            if($child==null) break;
            echo "<tr>";
            echo "<td>".$child->num_iid."</td>";
            echo "<td>".$child->title."</td>";
            echo "<td><img src='".$child->pic_url."'></td>";
            echo "<td>".$child->price."</td>";
            echo "<td>".$child->approve_status."</td>";
            echo "<td>".$child->cid."</td>";
            echo "<td>".$child->num."</td>";
            echo "<td><a href='ItemUpdate.php?iid=$child->num_iid'>编辑</a></td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=listing'>上架</a>"."</td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=delete'>删除</a>"."</td>";
            
            echo "</tr>";
        }
        echo "</table>";
        echo $my_page->myde_write1();
        
        if(isset($_POST['update'])){
            echo $_POST['update'];
        }
        
    }
    
    function echoInTable8($xml)
    {
        echo "<table border='1'>";
        echo "<tr class='title'><td align='center' colspan=9><font size=5>店主信息</font></td></tr>";
        echo "<tr><td>id</td><td>".$xml->user_id."</td></tr>";
        echo "<tr><td>uid</td><td>".$xml->uid."</td></tr>";
        echo "<tr><td>昵称</td><td>".$xml->nick."</td></tr>";
        echo "<tr><td>创建时间</td><td>".$xml->created."</td></tr>";
        echo "<tr><td>最近访问</td><td>".$xml->last_visit."</td></tr>";
        echo "<tr><td>类型</td><td>".$xml->type."</td></tr>";
        echo "<tr><td>状态</td><td>".$xml->status."</td></tr>";
        echo "</table>";
    }
    
    function echoInTable10()
    {
        echo <<<EOT
        <script language="javascript">
        function inputOnlyNum(e){
            e.value=e.value.replace(/[^1234567890-]+/g,'');
        }
        </script>
EOT;
        
        $xmlArray = func_get_args();     //获取参数，返回参数数组
        $xml = $xmlArray[0];
        
        include_once ("TFPage.php"); //分页类
        @$page=$_GET['page'];
        if(!$page){
            $page = 1;
        }
        $totail = count($xml->item);//记录总条数
        $number = 10;//每页显示条数
        
        $my_page=new PageClass($totail,$number,$page,'?page={page}');
        echo "<table border=1>";
        echo "<tr class='title'><td align='center' colspan=10><font size=5>商品同步</font></td></tr>";
        echo "<tr class='titleList'>";
        echo "<td>主店铺</td>";
        for($j = 1;$j<count($xmlArray);$j++){
            echo "<td>附属店铺".$j."</td>";
        }
        echo "<td>数量</td>";
        echo "<td>操作</td>";
        echo "</tr>";
        for($i=0;$i<$number;$i++){
            $child = $xml->item[($page-1)*$number+$i+1];
            if($child==null) break;
            echo "<tr>";
            echo "<td>".$child->title."</td>";
            for($j = 1;$j<count($xmlArray);$j++){
                echo "<td><form><select name='cars'>";
                foreach($xmlArray[$j]->item as $subChild){
                    echo "<option value='".$subChild->num_iid."'>".$subChild->title."</option>";
                }
                echo "</select></form></td>";
            }
            echo "<td><input onkeyup='inputOnlyNum(this);' value=".$child->num."></td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=listing'>编辑</a>"."</td>";
            
            echo "</tr>";
        }
        echo "</table>";
        echo $my_page->myde_write1();

        
        
    }
    
    function echoInTable11()
    {
 
        
        $xmlArray = func_get_args();     //获取参数，返回参数数组
        $xml = $xmlArray[0];
        
        include_once ("TFPage.php"); //分页类
        @$page=$_GET['page'];
        if(!$page){
            $page = 1;
        }
        $totail = count($xml->item);//记录总条数
        $number = 10;//每页显示条数
        
        $my_page=new PageClass($totail,$number,$page,'?page={page}');
        echo "<table border=1>";
        echo "<tr class='title'><td align='center' colspan=10><font size=5>商品同步</font></td></tr>";
        echo "<tr class='titleList'>";
        echo "<td>主店铺</td>";
        for($j = 1;$j<count($xmlArray);$j++){
            echo "<td>附属店铺".$j."</td>";
        }
        echo "<td>数量</td>";
        echo "<td>操作</td>";
        echo "</tr>";
        for($i=0;$i<$number;$i++){
            $child = $xml->item[($page-1)*$number+$i+1];
            if($child==null) break;
            echo "<tr>";
            echo "<td>".$child->title."</td>";
            for($j = 1;$j<count($xmlArray);$j++){
                echo "<td><form><select name='cars'>";
                foreach($xmlArray[$j]->item as $subChild){
                    echo "<option value='".$subChild->num_iid."'>".$subChild->title."</option>";
                }
                echo "</select></form></td>";
            }
            echo "<td><input onkeyup='inputOnlyNum(this);' value=".$child->num."></td>";
            echo "<td>"."<a href='ItemUpdate.php?iid=$child->num_iid&operation=listing'>编辑</a>"."</td>";
            
            echo "</tr>";
        }
        echo "</table>";
        echo $my_page->myde_write1();
        
        
        
    }
    

    
?>

