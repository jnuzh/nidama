<?php
/**
 * TOP API: taobao.qianniu.memo.update request
 * 
 * @author auto create
 * @since 1.0, 2014-02-20 17:02:53
 */
class QianniuMemoUpdateRequest
{
	/** 
	 * 备注内容.最长为2048
	 **/
	private $content;
	
	/** 
	 * 备忘ID
	 **/
	private $id;
	
	/** 
	 * 优先级。目前使用1表示标星，0表示未标星。
	 **/
	private $priority;
	
	/** 
	 * 0为不提醒，1为提醒。当remind_time有效时而此字段未指明默认为1.
	 **/
	private $remindFlag;
	
	/** 
	 * 提醒时间，时间的毫秒数。
	 **/
	private $remindTime;
	
	private $apiParas = array();
	
	public function setContent($content)
	{
		$this->content = $content;
		$this->apiParas["content"] = $content;
	}

	public function getContent()
	{
		return $this->content;
	}

	public function setId($id)
	{
		$this->id = $id;
		$this->apiParas["id"] = $id;
	}

	public function getId()
	{
		return $this->id;
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

	public function setRemindFlag($remindFlag)
	{
		$this->remindFlag = $remindFlag;
		$this->apiParas["remind_flag"] = $remindFlag;
	}

	public function getRemindFlag()
	{
		return $this->remindFlag;
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
		return "taobao.qianniu.memo.update";
	}
	
	public function getApiParas()
	{
		return $this->apiParas;
	}
	
	public function check()
	{
		
		RequestCheckUtil::checkMaxLength($this->content,2048,"content");
		RequestCheckUtil::checkNotNull($this->id,"id");
	}
	
	public function putOtherTextParam($key, $value) {
		$this->apiParas[$key] = $value;
		$this->$key = $value;
	}
}
