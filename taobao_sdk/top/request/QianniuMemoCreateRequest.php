<?php
/**
 * TOP API: taobao.qianniu.memo.create request
 * 
 * @author auto create
 * @since 1.0, 2014-02-20 17:02:53
 */
class QianniuMemoCreateRequest
{
	/** 
	 * 使用此接口的入口标记。
	 **/
	private $bizSysId;
	
	/** 
	 * 备忘的内容
	 **/
	private $content;
	
	/** 
	 * 优先级。当前用1表示标星，0表示未标星。
	 **/
	private $priority;
	
	/** 
	 * 提醒时间。
	 **/
	private $remindTime;
	
	private $apiParas = array();
	
	public function setBizSysId($bizSysId)
	{
		$this->bizSysId = $bizSysId;
		$this->apiParas["biz_sys_id"] = $bizSysId;
	}

	public function getBizSysId()
	{
		return $this->bizSysId;
	}

	public function setContent($content)
	{
		$this->content = $content;
		$this->apiParas["content"] = $content;
	}

	public function getContent()
	{
		return $this->content;
	}

	public function setPriority($priority)
	{
		$this->priority = $priority;
		$this->apiParas["priority"] = $priority;
	}

	public function getPriority()
	{
		return $this->priority;
	}

	public function setRemindTime($remindTime)
	{
		$this->remindTime = $remindTime;
		$this->apiParas["remind_time"] = $remindTime;
	}

	public function getRemindTime()
	{
		return $this->remindTime;
	}

	public function getApiMethodName()
	{
		return "taobao.qianniu.memo.create";
	}
	
	public function getApiParas()
	{
		return $this->apiParas;
	}
	
	public function check()
	{
		
		RequestCheckUtil::checkNotNull($this->content,"content");
		RequestCheckUtil::checkMaxLength($this->content,2048,"content");
	}
	
	public function putOtherTextParam($key, $value) {
		$this->apiParas[$key] = $value;
		$this->$key = $value;
	}
}
