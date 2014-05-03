<?php
    include("header.php");
    ?>





<?php
    echo "<div class='column'>";

    echo "<h2>黑历史，此页面非法</h2>";
    
    echo <<<EOT
    <ul>
    <p>代码相关问题</p>
    <li>问题一：淘宝API传来的数据都是SimpleXML对象格式，所以该应用完全是用SimpleXML来存储数据。对于数据库的使用暂未考虑，对用XML格式所带来的问题也暂未考虑。</li>
    <br/>
    <li>问题五：关于“订单的处理，新的订单同步。送仓库，清单，快递。”对于订单的处理，实际上涉及到的是商品的数量？由于淘宝商品设定了【拍下减库存】，所以订单还需要做什么处理吗？送仓库、清单、快递实际上要做什么不是很清楚。</li>
    <br/>
   
    </ul>
EOT;
    
    
    echo "</div>";
    
    ?>
























<?php
    include("footer.php");
    ?>