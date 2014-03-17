<?php
/**
 * TOP API: alibaba.member.userIdTomemberId.convert request
 * 
 * @author auto create
 * @since 1.0, 2014-02-20 17:02:53
 */
class AlibabaMemberUserIdTomemberIdConvertRequest
{
	/** 
	 * userId
	 **/
	private $userId;
	
	private $apiParas = array();
	
	public function setUserId($userId)
	{
		$this->userId = $userId;
		$this->apiParas["user_id"] = $userId;
	}

	public function getUserId()
	{
		return $this->userId;
	}

	public function getApiMethodName()
	{
		return "alibaba.member.userIdTomemberId.convert";
	}
	
	public function getApiParas()
	{
		return $this->apiParas;
	}
	
	public function check()
	{
		
		RequestCheckUtil::checkNotNull($this->userId,"userId");
	}
	
	public function putOtherTextParam($key, $value) {
		$this->apiParas[$key] = $value;
		$this->$key = $value;
	}
}
