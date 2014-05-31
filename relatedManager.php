<?php
    include("header.php");
   

    
    echo "<div class='column'>";
    
    include("relatedShowAjax.php");
    
    echo "</div>";
    
    
    echo "<div class='column four'>";
    
    //echo "<h2>完成编辑后必须点击同步才会生效</h2>";
    
echo <<<EOT
    <script>
    function submitSyn(){
        //需要同步文件
    }
    </script>
EOT;
    
    

    echo "<input type='submit' style='width:111px;height:111px;font-size:20px;' value='更新同步' onclick='submitSyn()'/>";

    echo "<input type='submit' style='width:111px;height:111px;font-size:20px;' value='自动关联' onclick='submitSyn()'/>";
    
    echo "</div>";
    
    
    include("footer.php");
    ?>