<?php
//签名函数
function createSign ($paramArr) {
     global $appSecret;
     $sign = $appSecret;
     ksort($paramArr);
     foreach ($paramArr as $key => $val) {
         if ($key != '' && $val != '') {
             $sign .= $key.$val;
         }
     }
     $sign.=$appSecret;
     $sign = strtoupper(md5($sign));
     return $sign;
}
//组参函数
function createStrParam ($paramArr) {
     $strParam = '';
     foreach ($paramArr as $key => $val) {
     if ($key != '' && $val != '') {
             $strParam .= $key.'='.urlencode($val).'&';
         }
     }
     return $strParam;
}
?>
