<?php


/**
 * Add one simplexml to another
 *
 * @param object $simplexml_to
 * @param object $simplexml_from
 * @author Boris Korobkov
 * @link http://www.ajaxforum.ru/
 */
function append_simplexml(&$simplexml_to, &$simplexml_from)
{
    if($simplexml_from[0] == NULL) return;//自己添加的，防止报空的警告
    foreach ($simplexml_from->children() as $simplexml_child)
    {
        $simplexml_temp = $simplexml_to->addChild($simplexml_child->getName(), (string) $simplexml_child);
        foreach ($simplexml_child->attributes() as $attr_key => $attr_value)
        {
            $simplexml_temp->addAttribute($attr_key, $attr_value);
        }
       
        append_simplexml($simplexml_temp, $simplexml_child);
    }
}
    function XF($xml){
        return $xml[0];
    }
?>   