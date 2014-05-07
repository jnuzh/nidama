<?php
    include("header.php");
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");
    include_once("EchoHelper.php");
    include_once("MySQLHelper.php");
    
    echo "<div class='column'>";
    

    $_SESSION['username'] = "sandbox_motherfun";
    $username = $_SESSION['username'];
    
    $users = simplexml_load_file('users_data.xml');
    $user = XF($users->xpath("user[username='$username']"));
    echo "<h2>欢迎".$user->username."使用淘宝商品数据同步器</h2>";

    
    echo "<br/>";
    echo <<<EOT
    

    
    
    
    <ul>
    <li>该应用可以用于已有多家店铺的数据同步</li>
    <br/>
    <li>进入【账户组别】后，可以查看当前组别号，组别是指能够相互同步商品数据的店铺组，该店铺组至少会有当前账户的店铺。一开始只有当前账户的店铺，想要添加其他店铺，则需要让其他店铺的店主登录指定网址授权并填入您的组别号。</li>
    <br/>
    <li>进入【关联商品】后，可以查看当前组别号的关联商品，可以新增、删除、修改。对于一个关联商品小组，只要有其中一间商品的数量属性发生改变，其他关联商品相应的数量属性也会跟随变动以保持一致。</li>
    <br/>
    <li>进入【店铺商品】后，可以查看该组别号下所有的店铺信息和商品信息，可以对商品进行上架、下架，以及对商品进行部分属性的修改。</li>
    <br/>
    <li>进入【关于】后，目前显示当前版本的问题和开发状况</li>
    </ul>
    
  

EOT;
    /*
    $mysql = new MFMySQL("nidama");
    $result = $mysql->query("select * from tbl_User");
    while($row = mysql_fetch_array($result))
    {
        echo $row['username'] . " " . $row['groupid'];
        echo "<br />";
    }

    $mysql->close();
    */
    echo "</div>";
    
    include("footer.php");
?>