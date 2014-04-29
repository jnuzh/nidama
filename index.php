<?php
    include("menu.php");
    include_once("TaobaoHelper.php");
    include_once("XmlHelper.php");
 
    echo "<div class='column'>";
    
    if(isset($_GET['SessionKey'])){
        $_SESSION['SessionKey'] =$_GET['SessionKey'];
    }
    
    

    
    $_SESSION['SessionKey'] = "61010075a1526931131d12f6b2cf03803641d47cf0142cf3629363321";
    $xml = simplexml_load_file('data.xml');
    $user = XF($xml->xpath("user[sessionkey='".$sessionkey."']"));
    echo "<h2>欢迎".$user->nick."使用淘宝商品数据同步器</h2>";

    
    echo "<br/>";
    echo <<<EOT
    <ul>
    <li>该应用可以用于已有多家店铺的数据同步，也可以用于新开分店时进行商品数据复制</li>
    <br/>
    <li>进入【个人账户】后，可以查看应用授权号，想要添加附属店铺，则需要让附属店铺的店主登录该网址填入您的应用授权号。</li>
    <br/>
    <li>进入【同步管理】后，可以查看当前主店铺与附属店铺的关联商品，可以新增、删除、修改。对于锁定同步的关联商品，只要有其中一间商品的数量属性发生改变，其他关联商品相应的数量属性也会跟随变动以保持一致。</li>
    <br/>
    <li>进入【店铺管理】后，可以查看主店铺与附属店铺的店铺信息和所有商品信息，可以对商品进行上架、下架，以及对商品进行部分属性的修改。</li>
    <br/>
    <li>进入【关于】后，目前显示当前版本的问题和开发状况</li>
    </ul>
EOT;

    echo "</div>";

    
    /*
    $parent_node = XF($xml->xpath("user[nick='sandbox_motherfun']"));
    $parent_id=XF($parent_node->xpath("@id"));
    $request_array = array(new MFRequest($parent_node->sessionkey));
    foreach ($xml->xpath("user[pid=".$parent_id."]") as $child) {
        $request_array[] = new MFRequest($child->sessionkey);
    }
    */
    
    /*
    
    foreach($request_array as $req){
        $msg = $req->tmcMessagesConsume();
        file_put_contents('msg.txt',$msg,FILE_APPEND);
    }
    
    */
    /*
    set_time_limit(0);
    while (true) {
        sleep(5);
        $msg = $request_array[0]->tmcMessagesConsume();
        file_put_contents('msg.txt',$msg,FILE_APPEND);
        ob_flush();
        flush();
        usleep(1000);
    }
    */
    //成功的案例
    //	print_r($request->itemAdd());
    
    
    //print_r($request->tmcMessageProduce());
    /*
     print_r($request->tmcUserGet());
     set_time_limit(0);
     while (true) {
     sleep(5);
     print_r($request->tmcMessagesConsume());
     echo "<br/>";
     ob_flush();
     flush();
     usleep(1000);
     }
     
     */
    
    
    include("foot.php");
?>