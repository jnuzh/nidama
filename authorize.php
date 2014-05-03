
<?php
    include("header.php");
    ?>

<?php



    if(isset($_GET['SessionKey'])){
        echo "<h3>您的店铺还未授权，请点击<a href='http://container.api.tbsandbox.com/container?appkey=1021759194'>授权</a></h3>";
    }else{
        echo "<h3>您当前的应用授权号为5123</h3>";
        $_SESSION['Authorize'] = "MainShop";
        echo "<p>如果是您的店铺是主店铺，请点击<a href='index.php'>进入应用</a></p></p>";
        echo "<p>如果您的店铺是附属店铺，请点击<a href='subsidiaryRegister.php'>设置主店铺</a></p>";
    }
    

?>


<?php
    include("footer.php");
    ?>