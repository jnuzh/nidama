<?php
/**
 * DCSDK的自定义函数列表
 * @author shaosheng
 */

//------------------------- php类 ---------

/**
 * 商品类
 */
class ItemDO
{
    /**
     * 商品ID
     */
    public $id = 1;
    /**
     * 价格
     */
    public $price = 12.10;
    /**
     * 商品标题
     */
    public $title = "商品标题";
    /**
     * 商品所属的卖家ID，long型
     */
    public $ownerId = 1;
    /**
     * 商品图片URL
     */
    public $picUrl = "http://www.taobao.com/xxx.gif";
    /**
     * 商品被收藏的次数
     */
    public $collectedCount = 2;
    /**
     * 累计销售数量
     */
    public $soldCount = 2;
    /**
     * 宝贝评论数，只对B2C商品有效
     */
    public $commentCount = 2;
    /**
     * 所属的店铺分类
     */
    public $shopCategoryId = array(1, 2);

    /**
     *  根据传递的图片象素获取图片，图片大小支持：
     *  80x80, b，220x220, 310x310, 60x60, 40x40, 160x160, 100x100,
     *  120x120，620x10000
     * @param int $height 图片像素高，可以使整数类型,默认160
     * @param int $width  图片像素宽，可以使整数类型，默认160
     *  如果图片像素大小错误的话，函数返回""字符串。
     *
     */
    public function getPicUrl($height = 160, $width = 160)
    {
        return "";
    }

    /**
     *  根据传递的图片象素获取图片，图片大小支持：
     *  80x80, b，220x220, 310x310, 60x60, 40x40, 160x160, 100x100,
     *  120x120，620x10000
     * @param height 图片像素高，可以使整数类型,默认160
     * @param width  图片像素宽，可以使整数类型，默认160
     *  如果图片像素大小错误的话，函数返回""字符串。
     */
    public function getPictureURL($height = 160, $width = 160)
    {
        return $this->getPicUrl($height, $width);
    }
}

/**
 * 店铺类
 */
class ShopDO
{
    /**
     * 店铺ID
     */
    public $id = 1;
    /**
     * 店铺标题
     */
    public $title = "店铺标题";
    /**
     * 店铺主营
     */
    public $mainBusiness = "店铺主营";
    /**
     * 开店时间
     */
    public $startTime = "2008-03-05";
    /**
     * 所属的卖家ID
     */
    public $ownerId = 1;
    /**
     * 所属的卖家Nick
     */
    public $ownerNick = "雷卷";
    /**
     * 店标URL
     */
    public $logoUrl = "http://logo.taobao.com/xxx.jpg";
    /**
     * 新版店铺LOGO
     */
    public $shopLogo = "http://log.taobao.com/xxx.jpg";
    /**
     * 宝贝数量
     */
    public $itemCount = 22;
    /**
     * 收藏人气：被收藏的次数
     */
    public $collectedCount = 100;
    /**
     * 店铺域名
     */
    public $domainName = "foobar.com";
    /**
     * 店铺介绍
     */
    public $introduction = "店铺介绍";
    /**
     * 店铺公告
     */
    public $bulettin = "店铺公告";
}

/**
 * 用户类
 */
class UserDO
{
    /**
     * 用户ID
     */
    public $id = 1;
    /**
     * 注册时间
     */
    public $registrationDate = "2008-03-05";
    /**
     * Nick
     */
    public $nick = "雷卷";
    /**
     * 国家
     */
    public $country = "中国";
    /**
     * 省
     */
    public $province = "浙江";
    /**
     * 城市
     */
    public $city = "杭州";
    /**
     * 信用
     */
    public $credit = 2222;
    /**
     * 好评率
     */
    public $goodRate = 1234;
}

/**
 * 友情链接对象
 */
class FriendLinkDO
{
    /**
     * ID
     */
    public $id = 11;
    /**
     * 所属的卖家ID
     */
    public $userId = 1;
    /**
     * 链接名称
     */
    public $title = "链接名称";
    /**
     * 链接地址
     */
    public $url = "http://www.taobao.com/xxx";
}

/**
 * 链接类
 */
class LinkDO
{
    /**
     * 链接地址
     */
    public $text = "链接名称";
    /**
     * 链接地址
     */
    public $href = "http://www.taobao.com/xxx";
    /**
     * target，2表示新窗口
     */
    public $target = 1;
    /**
     * 高亮标识
     */
    public $highLight = true;
}

/**
 * 店铺类目类
 */
class ShopCategoryDO
{
    /**
     * ID
     */
    public $id = 122;
    /**
     * 类目名称
     */
    public $name = "类目名称";
    /**
     * 类目图标
     */
    public $iconUrl = "类目图标URL";
    /**
     * 父类目ID
     */
    public $parentId = 100;
    /**
     * 所属的店铺ID
     */
    public $shopId = 1;
}

/**
 * Module渲染类
 */
class ModuleRender
{
    /**
     * 添加参数
     * @param  String $name 参数名
     * @param  $value 参数值
     * @return ModuleRender 自身对象
     */
    public function addParam($name, $value)
    {
        return $this;
    }
}

/**
 * 商品管理类
 */
class ItemManager
{
    /**
     * 加载多个商品
     * @param  array $idList 商品id列表
     * @param  String $sortType 排序类型
     * @return array 商品列表
     */
    public function queryByIds($idList, $sortType)
    {
        return array(new ItemDO());
    }

    /**
     * 添加参数
     * @param  number $id 商品id
     * @return ItemDO 商品对象
     */
    public function queryById($id)
    {
        return new ItemDO();
    }

    /**
     * 根据店铺类目ID查询该类目下的商品
     * @param  array $catId 商品id列表
     * @param  String $sortType 排序类型
     * @param  int $count 返回最多的条目数
     * @return array 商品列表
     */
    public function queryByCategory($catId, $sortType, $count)
    {
        return array(new ItemDO());
    }

    /**
     * 根据关键字查找店铺内商品
     * @param  String $keyword 关键字
     * @param  String $sortType 排序类型
     * @param  int $count 返回最多的条目数
     * @return array 商品列表
     */
    public function queryByKeyword($keyword, $sortType, $count)
    {
        return array(new ItemDO());
    }
}

/**
 *shop manager
 */
class ShopManager
{
    /**
     * 查找店铺的页面列表
     * @return array 页面列表，对象为LinkDO
     */
    public function getShopPageLinks()
    {
        return array();
    }
}

/**
 * 店铺类目管理类
 */
class ShopCategoryManager
{
    /**
     * 根据ID查找类目对象
     * @param  int $id 类目ID
     * @return ShopCategoryDO 类目对象
     */
    public function queryById($id)
    {
        return new ShopCategoryDO();
    }

    /**
     * 根据类目ID查找其子类目
     * @param  int $catId 类目ID
     * @return array 类目列表
     */
    public function querySubCategories($catId)
    {

    }

    /**
     * 查找所有类目，包括子类目
     * @return array 类目列表
     */
    public function queryAll()
    {
        return array(new ShopCategoryDO());
    }
}

/**
 * 友情链接管理器
 */
class FriendLinkManager
{
    /**
     * 查询所有的链接
     * @return array 友情链接列表
     */
    public function queryAllLinks()
    {
    }
}

/**
 * uri 生成管理器
 */
class URIManager
{
    /**
     * 生成宝贝详情页的url地址
     *
     * @param  ItemDO $item  宝贝对象
     * @return String  详情页地址
     */
    public function detailURI($item)
    {
        return "item.html?id=" . $item->id;
    }

    /**
     * 当前店铺的搜索页面URL
     *
     * @return String 搜索页面url
     */
    public function searchURI()
    {
        return "list.htm";
    }

    /**
     * 生成评价页面url地址
     * @return String 评价页的url地址
     */
    public function rateURI()
    {
    }

    /**
     * 店铺介绍页面的uri地址
     * @return String 店铺介绍URL地址
     */
    public function shopIntrURI()
    {
    }

    /**
     * 店铺介绍页面的uri地址
     * @param  $category ShopCategoryDO  shop category
     * @return String 店铺介绍URL地址
     */
    public function shopCategoryURI($category)
    {

    }

    /**
     * 生成主旺旺的HTML code.
     *
     * @param $userNick 旺旺帐号
     */
    public function contactTag($userNick)
    {
        return "";
    }

    /**
     * 生成客服旺旺的HTML code.
     * @param $userNick 旺旺帐号
     * @param $alternativeMessage 图片替换信息，如果旺旺点灯的图片不能正常显示时，提示的文字信息
     * @param $style 旺旺点灯图片的风格，默认值为1（大图标），2为小图标
     * @param $isDistributed 是否支持 E客服分流，默认值为false(不支持），true为支持客服分流
     */
    public function supportTag($userNick, $alternativeMessage = "", $style = 1, $isDistributed = false)
    {
        return "";
    }
}

//---------------- 全局对象 ------------------------

/**
 * 模块参数对象，一个Map结构对象
 */
$_MODULE = array("param" => 'value');

/**
 * 店铺管理全局对象
 */
$shopManager = new ShopManager();
/**
 * 商品管理全局对象
 */
$itemManager = new ItemManager();

/**
 * 店铺类目管理全局对象
 */
$shopCategoryManager = new ShopCategoryManager();
/**
 * 友情链接管理器
 */
$friendLinkManager = new FriendLinkManager();
/**
 * URI管理器全局对象
 */
$uriManager = new URIManager();
/**
 * 用户对象
 */
$_user = new UserDO();

/**
 * 店铺对象
 */
$_shop = new ShopDO();


//---------------------- 全局函数 -------------------
/**
 * 包含模块列表
 * @param string $section_name section名称
 * @param string $module_list 样例模块列表
 *    array(array('id'=>'textbox','domId'=>'xxx'),array('shortname'=>'shop.topList','version'=>'1.0-common','domId'=>2))
 */
function include_modules($section_name, $module_list)
{
    return "";
}

/**
 * 包含模板内的模块
 * @param string $module_name 模块名称
 * @param string $dom_id 模块的dom ID
 * @return ModuleRender  模块渲染后的代码
 */
function include_local_module($module_name, $dom_id)
{
    return new ModuleRender();
}

/**
 * 包含系统模块
 * @param string $module_short_name 系统模块的short name
 * @param string $version 系统模块的版本号
 * @param string $dom_id 模块的Dom ID
 * @return ModuleRender 模块渲染后的代码
 */
function include_system_module($module_short_name, $version, $dom_id)
{
    return new ModuleRender();
}

?>
