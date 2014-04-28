<?php
    include("menu.php");
    ?>





<?php
    echo "<p>本页面提供授权功能</p>";
    echo "<p>注意，一旦授权，主店铺将有权对您的店铺进行各种商品操作。</p>";
    echo "<p>因主店铺的操作而对您店铺所造成的影响，本应用一概不负责任。</p>";
    
    echo "<form action='http://container.api.tbsandbox.com/container?appkey=1021759194' method='get'>";
    echo "<input type='hidden' name='operation' value='update'/>";
    echo "<h3>请输入主店铺的应用授权号</h3> <input type='text' name='authorizeId' />";
    echo "<input type='submit' value='授权'/>";
    echo "</form>";


?>
























<?php
    include("foot.php");
    ?>