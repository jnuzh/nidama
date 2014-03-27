
<?php
header("Content-Type: text/html; charset=gb2312");
require_once 'util.php';
$appKey = 'test';
$appSecret = 'test';
//参数数组
$paramArr = array(
     'app_key' => $appKey,
     'method' => 'taobao.user.get',
     'format' => 'json',
     'v' => '2.0',
     'sign_method'=>'md5',
     'timestamp' => date('Y-m-d H:i:s'),
     'fields' => 'nick,type,buyer_credit,seller_credit',
     'nick' => 'sandbox_motherfun'
);
//生成签名
$sign = createSign($paramArr);
//组织参数
$strParam = createStrParam($paramArr);
$strParam .= 'sign='.$sign;
//访问服务
$url = 'http://gw.api.tbsandbox.com/router/rest?'.$strParam;

echo $url;
echo "<br><br>";
$result = file_get_contents($url);
$result = json_decode($result);
echo "json的结构为:";
print_r($result);
echo "<br>";
echo "用户名称为:".$result->user_get_response->user->nick;
echo "<br>";
echo "买家信用等级为:".$result->user_get_response->user->buyer_credit->level;
?>

