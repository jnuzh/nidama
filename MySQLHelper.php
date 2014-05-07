

<?php

    class MFMySQL
    {
        private $con;
        
        function __construct($database)
        {

            $host            = "localhost";
            $username        = "root";
            $password        = "";
            $this->con             = mysql_connect($host, $username, $password);
            if (!$this->con) {
                die('Could not connect:' . mysql_error());
            }
            mysql_query("use $database", $this->con);
            
        }
        
        function query($query_str){
            return mysql_query($query_str);
        }
        
        function close(){
            mysql_close($this->con);
        }
    }
        
?>