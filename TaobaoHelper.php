<?php
include("taobao_sdk/TopSdk.php");
    include_once("XmlHelper.php");

    
class MFRequest
{
    public $center;
    private $sessionKey;
    private $error;

    function __construct($sessionKey)
    {
        $this->center            = new TopClient;
        $this->center->appkey    = "1021759194";
        $this->center->secretKey = "sandbox28a555dbe54c7657fbd54a662";
        $this->sessionKey        = $sessionKey;
    }
    
    function setAppkey($appKey)
    {
        $this->center->appKey = $appKey;
        
    }
    
    function setSecretKey($secretKey)
    {
        $this->center->secretKey = $secretKey;
    }
    
    function setSessionKey($sessionKey)
    {
        $this->center->sessionKey = $sessionKey;
    }
    
    function shopGet($nick)
    {
        $req = new ShopGetRequest;
        $req->setFields("sid,cid,title,nick,desc,bulletin,pic_path,created,modified");
        $req->setNick($nick);
        $resp = $this->center->execute($req);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->shop;
        }
    }
    
    function userGet()
    {
        $req = new UserGetRequest;
        $req->setFields("user_id,uid,nick,sex,buyer_credit,seller_credit,location,created,last_visit,birthday,type,status,email");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->user;
        }
    }
    
    function sellerGet()
    {
        $req = new UserSellerGetRequest;
        $req->setFields("user_id,nick,sex,seller_credit,type,has_more_pic,item_img_num,item_img_size,prop_img_num,prop_img_size,auto_repost,promoted_type,status,alipay_bind,consumer_protection,avatar,liangpin,sign_food_seller_promise,has_shop");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->user;
        }
    }
    
    function itemsListGet()
    {
        $req = new ItemsListGetRequest;
        $req->setFields("detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual");
        $req->setNumIid(3838293428);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }
    
    function itemsOnsaleGet()
    {
        $req = new ItemsOnsaleGetRequest;
        //$req->setFields("approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id");
         $req->setFields("approve_status,num_iid,title,nick,cid,num,price,seller_cids,pic_url");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->items;
        }
    }
    
    function itemsInventorGet()
    {
        $req = new ItemsInventoryGetRequest;
        $req->setFields("approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->items;
        }
    }
    
    function itemsAllGet(){
        $xml = $this->itemsOnsaleGet();
        append_simplexml($xml,$this->itemsInventorGet());
        return $xml;
    }
    
    function itemGet($numIid)
    {
        $req = new ItemGetRequest;
        $req->setFields("detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual");
        $req->setNumIid($numIid);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    
    function itemUpdate($numIid,$num){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setNum($num);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    
    function itemUpdateNum($numIid,$num){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setNum($num);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    function itemUpdateTitle($numIid,$title){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setTitle($title);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    function itemUpdateDesc($numIid,$desc){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setDesc($desc);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    
    function itemUpdateDelisting($numIid){
        $req = new ItemUpdateDelistingRequest;
        $req->setNumIid(intval($numIid));
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    
    function itemUpdateListing($numIid,$num){
        $req = new ItemUpdateListingRequest;
        $req->setNumIid(intval($numIid));
        $req->setNum(intval($num));
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item;
        }
    }
    
    function itemcatsAuthorizeGet()
    {
        $req = new ItemcatsAuthorizeGetRequest;
        $req->setFields("brand.vid,brand.name,item_cat.cid,item_cat.name,item_cat.status,item_cat.sort_order,item_cat.parent_cid,item_cat.is_parent");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
        
    }
    
    function itemcatsGet()
    {
        $req = new ItemcatsGetRequest;
        $req->setFields("cid,parent_cid,name,is_parent");
        $req->setParentCid(0);
        $resp = $this->center->execute($req);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->item_cats;
        }
    }
    
    function itemAdd()
    {
        $req = new ItemAddRequest;
        $req->setNum(100);
        $req->setPrice("50");
        $req->setType("fixed");
        $req->setStuffStatus("new");
        $req->setTitle("沙箱测试：妹子玩偶（铃仙）");
        $req->setDesc("这是东方系列的玩偶。");
        $req->setLocationState("广东");
        $req->setLocationCity("珠海");
        $req->setCid(50000802);
        $req->setApproveStatus("instock"); 
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }
    
    function itemDelete($numIid){
        $req = new ItemDeleteRequest;
        $req->setNumIid(intval($numIid));
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
	}
    
    
    function tmcMessagesConsume()
    {
        $req = new TmcMessagesConsumeRequest;
        $req->setQuantity(100);
        $resp = $this->center->execute($req);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }
    
    function tmcUserPermit(){
		$req = new TmcUserPermitRequest;
		$req->setTopics("taobao_item_ItemAdd,taobao_item_ItemUpdate,taobao_item_ItemDelete,taobao_item_ItemUpshelf,taobao_item_ItemDownshelf");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }

	
	function tmcUserGet(){
        $req = new TmcUserGetRequest;
        $req->setFields("user_nick,topics,user_id,is_valid,created,modified");
        $req->setNick("sandbox_motherfun");
        $resp = $this->center->execute($req);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
	}
	
	function tmcMessageProduce(){
        $req = new TmcMessageProduceRequest;
        $req->setTopic("taobao_trade_TradeCreate");
        $req->setContent("{'tid':2895732958732,'seller_nick':'sandbox_motherfun'}");
        $resp = $this->center->execute($req);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
	}
    
    
    function tradesSoldGet(){
        $req = new TradesSoldGetRequest;
        $req->setFields("seller_nick,buyer_nick,title,type,created,sid,tid,seller_rate,buyer_rate,status,payment,rate_status,orders.title,orders.pic_path,orders.price,orders.num,orders.iid,orders.num_iid");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->trades;
        }
    }
    
    function tradeGet($tid){
        $req = new TradeGetRequest;
        $req->setFields("orders.title,orders.price, orders.num, orders.num_iid, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee,  orders.item_meal_name, orders.outer_iid, buyer_nick, title, type, created, tid, seller_rate, buyer_rate, status,buyer_message");
        $req->setTid($tid);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->trade;
        }
    }
    
    function tradeFullinfoGet($tid){
        $req = new TradeFullinfoGetRequest;
        $req->setFields("orders.title,orders.price, orders.num, orders.num_iid, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee,  orders.item_meal_name, orders.outer_iid, buyer_nick, title, type, created, tid, seller_rate, buyer_rate, status,buyer_message,receiver_name, receiver_state, receiver_city, receiver_district, receiver_address, receiver_zip, receiver_mobile, receiver_phone,buyer_area");
        $req->setTid($tid);
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->trade;
        }
    }
    
    function logisticsCompaniesGet(){
        $req = new LogisticsCompaniesGetRequest;
        $req->setFields("id,code,name,reg_mail_no");
        $req->setIsRecommended("true");
        $req->setOrderMode("offline");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->logistics_companies;
        }
    }

    function logisticsAddressSearch(){
        $req = new LogisticsAddressSearchRequest;
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp->addresses;
        }
    }

    
    
    function logisticsConsignOrderCreateandsend($user_id,$lcomId,$tid,$sInfo,$rInfo){
        $req = new LogisticsConsignOrderCreateandsendRequest;
        $req->setUserId($user_id);
        $req->setOrderSource(1);
        $req->setOrderType(0);
        $req->setLogisType(1);
        $req->setCompanyId($lcomId); //物流公司ID
        $req->setTradeId($tid);   //交易流水号
        
        $req->setSName($sInfo->contact_name);   //发件人名称
        $req->setSAreaId($sInfo->area_id);  //发件人区域ID？？？？？
        $req->setSAddress($sInfo->addr); //发件人街道地址
        $req->setSZipCode($sInfo->zip_code);   //发件人邮编
        $req->setRMobilePhone($sInfo->phone);
        $req->setRTelephone($sInfo->mobile_phone);
        $req->setSProvName($sInfo->province);
        $req->setSCityName($sInfo->city);
        $req->setSDistName($sInfo->country);
        
        $req->setRName($rInfo->receiver_name);  //收件人名称
        $req->setRAreaId(0756);  //收件人区域？？？？？
        $req->setRAddress($rInfo->receiver_address); //收件人街道地址
        $req->setRZipCode($rInfo->receiver_zip); //收件人邮编
        $req->setRMobilePhone($rInfo->receiver_phone);
        $req->setRTelephone($rInfo->receiver_mobile);
        $req->setRProvName($rInfo->receiver_state);  //省
        $req->setRCityName($rInfo->receiver_city);  //市
        $req->setRDistName($rInfo->receiver_district);  //区
        
       
        $req->setItemJsonString("[{'itemName':'ssss','singlePrice':10,'itemCount':12},{'itemName':'xxxxx',singlePrice:10,itemCount:12}]");  //物品的json数据


        
        $resp = $this->center->execute($req, $this->sessionKey);
        echo "ok";
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }
    
    
    
    function print_error(){
        if($this->error){
            echo "<br/>出现错误！返回为：";
            print_r($this->error);
            echo "<br/>";
        }
    }
    
    /////////////////////开发人员使用
    function itemAddWithTitle($title)
    {
        $req = new ItemAddRequest;
        $req->setNum(100);
        $req->setPrice("50");
        $req->setType("fixed");
        $req->setStuffStatus("new");
        $req->setTitle("沙箱测试：".$title);
        $req->setDesc("这是沙箱测试用的商品。");
        $req->setLocationState("广东");
        $req->setLocationCity("珠海");
        $req->setCid(50000802);
        $req->setApproveStatus("onsale");
        $resp = $this->center->execute($req, $this->sessionKey);
        if($resp->getName()=="error_response"){
            $this->error = $resp;
            return null;
        }else{
            return $resp;
        }
    }
    
    function itemsAddWithTitle($title){
        $tag    =   'A';
        for($i = 0;$i<10;$i++){
            $this->itemAddWithTitle($title.($tag++));
        }
    }
}
?>