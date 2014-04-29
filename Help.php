<?php
    include("menu.php");
    ?>





<?php
    echo "<div class='column'>";

    
    
    echo <<<EOT
    <ul>
    <li>问题一：淘宝API传来的数据都是SimpleXML对象格式，所以该应用完全是用SimpleXML来存储数据。对于数据库的使用暂未考虑，对用XML格式所带来的问题也暂未考虑。</li>
    <br/>
    <li>问题二：由于对PHP不熟练，显示数据的更新基本上都是整个页面的刷新来实现，暂时都是用get方法，对于表单重复提交的问题未进行处理。对部分内容的刷新开始转用AJAX重写。</li>
    <br/>
    <li>问题三：在同步管理方面，现在还未对数据进行同步。需要确认正确性，现在的思路是这样的。在同步管理页面中显示的关联商品都是出于同步锁定的状态。每当任何一个关联商品出现了“ItemUpate,ItemAdd,ItemDelete,TradeSuccess”等事件时，淘宝开放平台会发送这些事件消息到nidama.com这个回调地址，然后我们就在回调地址所在页面index.php中处理这些事件消息。</li>
    <br/>
    </ul>
EOT;
    
    
    echo "</div>";
    
    ?>
























<?php
    include("foot.php");
    ?>