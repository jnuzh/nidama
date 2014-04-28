<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta content="ellen" name="author">
<link rev="made" href="">
<link href="page.css" type="text/css" rel="stylesheet">

<title>淘宝应用开发</title>
</head>

<body>
<table border="1" width="600" cellspacing="1" align="center">
<tr>
<td>地址</td>
<td>百分比</td>
<td>点击量</td>
<td>时间</td>
</tr>
<?php
    include_once ("TFPage.php"); //分页类
    @$page=$_GET['page'];
    if(!$page){
        $page = 1;
    }
    $totail = 100;//记录总条数
    $number = 5;//每页显示条数
    
    $my_page=new PageClass($totail,$number,$page,'?page={page}');
    
    $row = array(
                 "id" => "23",
                 "sex" => "female",
                 "name"=>"RedFun",
                 "time"=>"Monday",
                 );

    
    for($i=1;$i<100;$i++){
        $row['id']=$i;
        $rows[$i]=$row;
    }

    
    for($i=0;$i<$number;$i++){
        $x = $rows[($page-1)*$number+$i+1];
        
        ?>
<tr>
<td><?php echo $x['id'];?></td>
<td><?php echo $x['sex'];?></td>
<td><?php echo $x['name'];?></td>
<td><?php echo $x['time'];?></td>
</tr>
<?php } ?>
</table>
<?php
    echo $my_page->myde_write1();//输出分页
    ?>
</body>
</html>