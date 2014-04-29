<?php session_start();?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta content="ellen" name="author">
<link rev="made" href="">
<link href="page.css" type="text/css" rel="stylesheet">
<style type="text/css">
<!--
body {
    background-image: url(bg.png);
    <!--[if !IE 6]->
        position: relative;
        height: auto;
        min-height: 100%
    <![endif]-->
    
    <!--[if IE 6]->
        height:100%;/* IE在高度不够时会自动撑开层*/
    <![endif]-->
    
}
tr.navigator{
    background:transparent;
}
td.navigator{
    width: 200px;
}
a.navigator{
    font-size:30px;
    color:#ffffff;
}

.column{
   // outline:1px dashed red;
    float:left;
    margin:0 2%;
    padding:0 2%;
   // background:#9AC;
}
.one{
    width:20%;
    margin:0 0%;
    padding:0 2%;
}
.two{
    width:50%;
    border:1px solid gray;
    border-width:0 1px;
    margin:0 0%;
    padding:0 2%;
}
.three{

     width:10%;
}

.four{
width:30%;
}
.footer{
clear:left;
}
-->
</style>



<title>淘宝应用开发</title>
</head>
<body>
<div style='margin-top:150px; margin-bottom:50px; margin-left:2%; padding:0 2%;'>
<table>
<tr  class='navigator'>
<td class='navigator'><a class='navigator' href="index.php">主页</a></td>
<td class='navigator'><a class='navigator' href="user.php">个人账户</a></td>
<td class='navigator'><a class='navigator' href="manager.php">同步管理</a></td>

<?php
    include_once("XmlHelper.php");
    $sessionkey = $_SESSION['SessionKey'];
    $xml = simplexml_load_file('data.xml');
    $user = XF($xml->xpath("user[sessionkey='".$sessionkey."']"));
    echo "<td class='navigator'><a class='navigator' href = 'home.php?SessionKey=".$user->sessionkey."'>店铺管理</a></td>";
    ?>
<td class='navigator'><a class='navigator' href="Help.php">关于</a></td>
<tr>
</table>
</div>






