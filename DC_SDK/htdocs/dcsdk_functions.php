<?php
/**
 * DCSDK���Զ��庯���б�
 * @author shaosheng
 */

//------------------------- php�� ---------

/**
 * ��Ʒ��
 */
class ItemDO
{
    /**
     * ��ƷID
     */
    public $id = 1;
    /**
     * �۸�
     */
    public $price = 12.10;
    /**
     * ��Ʒ����
     */
    public $title = "��Ʒ����";
    /**
     * ��Ʒ����������ID��long��
     */
    public $ownerId = 1;
    /**
     * ��ƷͼƬURL
     */
    public $picUrl = "http://www.taobao.com/xxx.gif";
    /**
     * ��Ʒ���ղصĴ���
     */
    public $collectedCount = 2;
    /**
     * �ۼ���������
     */
    public $soldCount = 2;
    /**
     * ������������ֻ��B2C��Ʒ��Ч
     */
    public $commentCount = 2;
    /**
     * �����ĵ��̷���
     */
    public $shopCategoryId = array(1, 2);

    /**
     *  ���ݴ��ݵ�ͼƬ���ػ�ȡͼƬ��ͼƬ��С֧�֣�
     *  80x80, b��220x220, 310x310, 60x60, 40x40, 160x160, 100x100,
     *  120x120��620x10000
     * @param int $height ͼƬ���ظߣ�����ʹ��������,Ĭ��160
     * @param int $width  ͼƬ���ؿ�����ʹ�������ͣ�Ĭ��160
     *  ���ͼƬ���ش�С����Ļ�����������""�ַ�����
     *
     */
    public function getPicUrl($height = 160, $width = 160)
    {
        return "";
    }

    /**
     *  ���ݴ��ݵ�ͼƬ���ػ�ȡͼƬ��ͼƬ��С֧�֣�
     *  80x80, b��220x220, 310x310, 60x60, 40x40, 160x160, 100x100,
     *  120x120��620x10000
     * @param height ͼƬ���ظߣ�����ʹ��������,Ĭ��160
     * @param width  ͼƬ���ؿ�����ʹ�������ͣ�Ĭ��160
     *  ���ͼƬ���ش�С����Ļ�����������""�ַ�����
     */
    public function getPictureURL($height = 160, $width = 160)
    {
        return $this->getPicUrl($height, $width);
    }
}

/**
 * ������
 */
class ShopDO
{
    /**
     * ����ID
     */
    public $id = 1;
    /**
     * ���̱���
     */
    public $title = "���̱���";
    /**
     * ������Ӫ
     */
    public $mainBusiness = "������Ӫ";
    /**
     * ����ʱ��
     */
    public $startTime = "2008-03-05";
    /**
     * ����������ID
     */
    public $ownerId = 1;
    /**
     * ����������Nick
     */
    public $ownerNick = "�׾�";
    /**
     * ���URL
     */
    public $logoUrl = "http://logo.taobao.com/xxx.jpg";
    /**
     * �°����LOGO
     */
    public $shopLogo = "http://log.taobao.com/xxx.jpg";
    /**
     * ��������
     */
    public $itemCount = 22;
    /**
     * �ղ����������ղصĴ���
     */
    public $collectedCount = 100;
    /**
     * ��������
     */
    public $domainName = "foobar.com";
    /**
     * ���̽���
     */
    public $introduction = "���̽���";
    /**
     * ���̹���
     */
    public $bulettin = "���̹���";
}

/**
 * �û���
 */
class UserDO
{
    /**
     * �û�ID
     */
    public $id = 1;
    /**
     * ע��ʱ��
     */
    public $registrationDate = "2008-03-05";
    /**
     * Nick
     */
    public $nick = "�׾�";
    /**
     * ����
     */
    public $country = "�й�";
    /**
     * ʡ
     */
    public $province = "�㽭";
    /**
     * ����
     */
    public $city = "����";
    /**
     * ����
     */
    public $credit = 2222;
    /**
     * ������
     */
    public $goodRate = 1234;
}

/**
 * �������Ӷ���
 */
class FriendLinkDO
{
    /**
     * ID
     */
    public $id = 11;
    /**
     * ����������ID
     */
    public $userId = 1;
    /**
     * ��������
     */
    public $title = "��������";
    /**
     * ���ӵ�ַ
     */
    public $url = "http://www.taobao.com/xxx";
}

/**
 * ������
 */
class LinkDO
{
    /**
     * ���ӵ�ַ
     */
    public $text = "��������";
    /**
     * ���ӵ�ַ
     */
    public $href = "http://www.taobao.com/xxx";
    /**
     * target��2��ʾ�´���
     */
    public $target = 1;
    /**
     * ������ʶ
     */
    public $highLight = true;
}

/**
 * ������Ŀ��
 */
class ShopCategoryDO
{
    /**
     * ID
     */
    public $id = 122;
    /**
     * ��Ŀ����
     */
    public $name = "��Ŀ����";
    /**
     * ��Ŀͼ��
     */
    public $iconUrl = "��Ŀͼ��URL";
    /**
     * ����ĿID
     */
    public $parentId = 100;
    /**
     * �����ĵ���ID
     */
    public $shopId = 1;
}

/**
 * Module��Ⱦ��
 */
class ModuleRender
{
    /**
     * ��Ӳ���
     * @param  String $name ������
     * @param  $value ����ֵ
     * @return ModuleRender �������
     */
    public function addParam($name, $value)
    {
        return $this;
    }
}

/**
 * ��Ʒ������
 */
class ItemManager
{
    /**
     * ���ض����Ʒ
     * @param  array $idList ��Ʒid�б�
     * @param  String $sortType ��������
     * @return array ��Ʒ�б�
     */
    public function queryByIds($idList, $sortType)
    {
        return array(new ItemDO());
    }

    /**
     * ��Ӳ���
     * @param  number $id ��Ʒid
     * @return ItemDO ��Ʒ����
     */
    public function queryById($id)
    {
        return new ItemDO();
    }

    /**
     * ���ݵ�����ĿID��ѯ����Ŀ�µ���Ʒ
     * @param  array $catId ��Ʒid�б�
     * @param  String $sortType ��������
     * @param  int $count ����������Ŀ��
     * @return array ��Ʒ�б�
     */
    public function queryByCategory($catId, $sortType, $count)
    {
        return array(new ItemDO());
    }

    /**
     * ���ݹؼ��ֲ��ҵ�������Ʒ
     * @param  String $keyword �ؼ���
     * @param  String $sortType ��������
     * @param  int $count ����������Ŀ��
     * @return array ��Ʒ�б�
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
     * ���ҵ��̵�ҳ���б�
     * @return array ҳ���б�����ΪLinkDO
     */
    public function getShopPageLinks()
    {
        return array();
    }
}

/**
 * ������Ŀ������
 */
class ShopCategoryManager
{
    /**
     * ����ID������Ŀ����
     * @param  int $id ��ĿID
     * @return ShopCategoryDO ��Ŀ����
     */
    public function queryById($id)
    {
        return new ShopCategoryDO();
    }

    /**
     * ������ĿID����������Ŀ
     * @param  int $catId ��ĿID
     * @return array ��Ŀ�б�
     */
    public function querySubCategories($catId)
    {

    }

    /**
     * ����������Ŀ����������Ŀ
     * @return array ��Ŀ�б�
     */
    public function queryAll()
    {
        return array(new ShopCategoryDO());
    }
}

/**
 * �������ӹ�����
 */
class FriendLinkManager
{
    /**
     * ��ѯ���е�����
     * @return array ���������б�
     */
    public function queryAllLinks()
    {
    }
}

/**
 * uri ���ɹ�����
 */
class URIManager
{
    /**
     * ���ɱ�������ҳ��url��ַ
     *
     * @param  ItemDO $item  ��������
     * @return String  ����ҳ��ַ
     */
    public function detailURI($item)
    {
        return "item.html?id=" . $item->id;
    }

    /**
     * ��ǰ���̵�����ҳ��URL
     *
     * @return String ����ҳ��url
     */
    public function searchURI()
    {
        return "list.htm";
    }

    /**
     * ��������ҳ��url��ַ
     * @return String ����ҳ��url��ַ
     */
    public function rateURI()
    {
    }

    /**
     * ���̽���ҳ���uri��ַ
     * @return String ���̽���URL��ַ
     */
    public function shopIntrURI()
    {
    }

    /**
     * ���̽���ҳ���uri��ַ
     * @param  $category ShopCategoryDO  shop category
     * @return String ���̽���URL��ַ
     */
    public function shopCategoryURI($category)
    {

    }

    /**
     * ������������HTML code.
     *
     * @param $userNick �����ʺ�
     */
    public function contactTag($userNick)
    {
        return "";
    }

    /**
     * ���ɿͷ�������HTML code.
     * @param $userNick �����ʺ�
     * @param $alternativeMessage ͼƬ�滻��Ϣ�����������Ƶ�ͼƬ����������ʾʱ����ʾ��������Ϣ
     * @param $style �������ͼƬ�ķ��Ĭ��ֵΪ1����ͼ�꣩��2ΪСͼ��
     * @param $isDistributed �Ƿ�֧�� E�ͷ�������Ĭ��ֵΪfalse(��֧�֣���trueΪ֧�ֿͷ�����
     */
    public function supportTag($userNick, $alternativeMessage = "", $style = 1, $isDistributed = false)
    {
        return "";
    }
}

//---------------- ȫ�ֶ��� ------------------------

/**
 * ģ���������һ��Map�ṹ����
 */
$_MODULE = array("param" => 'value');

/**
 * ���̹���ȫ�ֶ���
 */
$shopManager = new ShopManager();
/**
 * ��Ʒ����ȫ�ֶ���
 */
$itemManager = new ItemManager();

/**
 * ������Ŀ����ȫ�ֶ���
 */
$shopCategoryManager = new ShopCategoryManager();
/**
 * �������ӹ�����
 */
$friendLinkManager = new FriendLinkManager();
/**
 * URI������ȫ�ֶ���
 */
$uriManager = new URIManager();
/**
 * �û�����
 */
$_user = new UserDO();

/**
 * ���̶���
 */
$_shop = new ShopDO();


//---------------------- ȫ�ֺ��� -------------------
/**
 * ����ģ���б�
 * @param string $section_name section����
 * @param string $module_list ����ģ���б�
 *    array(array('id'=>'textbox','domId'=>'xxx'),array('shortname'=>'shop.topList','version'=>'1.0-common','domId'=>2))
 */
function include_modules($section_name, $module_list)
{
    return "";
}

/**
 * ����ģ���ڵ�ģ��
 * @param string $module_name ģ������
 * @param string $dom_id ģ���dom ID
 * @return ModuleRender  ģ����Ⱦ��Ĵ���
 */
function include_local_module($module_name, $dom_id)
{
    return new ModuleRender();
}

/**
 * ����ϵͳģ��
 * @param string $module_short_name ϵͳģ���short name
 * @param string $version ϵͳģ��İ汾��
 * @param string $dom_id ģ���Dom ID
 * @return ModuleRender ģ����Ⱦ��Ĵ���
 */
function include_system_module($module_short_name, $version, $dom_id)
{
    return new ModuleRender();
}

?>
